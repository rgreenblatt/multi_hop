#!/usr/bin/env python3
"""
Evaluation script for addition problems using Claude WITHOUT reasoning (few-shot).
"""

import json
import re
import os
import asyncio
import random
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from response_cache import ResponseCache

# Load API keys
if "ANTHROPIC_API_KEY" not in os.environ:
    key_path = os.path.expanduser("~/.anthropic_api_key")
    try:
        with open(key_path, "r") as f:
            os.environ["ANTHROPIC_API_KEY"] = f.read().strip()
    except FileNotFoundError:
        ...

if "OPENAI_API_KEY" not in os.environ:
    key_path = os.path.expanduser("~/.openai_api_key")
    try:
        with open(key_path, "r") as f:
            os.environ["OPENAI_API_KEY"] = f.read().strip()
    except FileNotFoundError:
        ...

if "OPENROUTER_API_KEY" not in os.environ:
    key_path = os.path.expanduser("~/.openrouter_api_key")
    try:
        with open(key_path, "r") as f:
            os.environ["OPENROUTER_API_KEY"] = f.read().strip()
    except FileNotFoundError:
        ...

# Initialize clients
anthropic_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
openrouter_client = AsyncOpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# Initialize cache
response_cache = ResponseCache("caches/cache_addition.json")

# OpenAI models (chat API)
OPENAI_CHAT_MODELS = {
    "gpt-3.5-turbo-0125",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-0125-preview",
    "gpt-4-turbo-2024-04-09",
    "gpt-4-1106-preview",
    "gpt-4o-2024-08-06",
    "gpt-4o-2024-05-13",
    "gpt-4.1-2025-04-14",
    "gpt-5.1-2025-11-13",
    "gpt-5.2-2025-12-11",
}

# OpenRouter models
OPENROUTER_MODELS = {
    "deepseek/deepseek-chat-v3-0324",
    "deepseek/deepseek-v3.2",
    "qwen/qwen3-235b-a22b",
    "qwen/qwen3-235b-a22b-2507",
    "qwen/qwen3-coder",
    "qwen/qwen3-32b",
    "moonshotai/kimi-k2",
    "google/gemini-2.5-pro",
    "google/gemini-3-pro-preview",
}

# Gemini models (require special handling - no native thinking disable)
GEMINI_MODELS = {
    "google/gemini-2.5-pro",
    "google/gemini-3-pro-preview",
}

# Cost tracking
COST_TRACKER = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_creation_tokens": 0,
}

# Pricing per million tokens
PRICING = {
    "claude-opus-4-5-20251101": {
        "input": 15.0,
        "output": 75.0,
        "cache_read": 1.5,
        "cache_write": 18.75,
    },
    "claude-opus-4-20250514": {
        "input": 15.0,
        "output": 75.0,
        "cache_read": 1.5,
        "cache_write": 18.75,
    },
    "claude-sonnet-4-20250514": {
        "input": 3.0,
        "output": 15.0,
        "cache_read": 0.3,
        "cache_write": 3.75,
    },
    "claude-sonnet-4-5-20250929": {
        "input": 3.0,
        "output": 15.0,
        "cache_read": 0.3,
        "cache_write": 3.75,
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.8,
        "output": 4.0,
        "cache_read": 0.08,
        "cache_write": 1.0,
    },
}


def load_problems(filepath):
    """Load problems from JSONL file."""
    problems = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            problems.append(json.loads(line))
    return problems


def select_few_shot_problems(problems, k_shot=10):
    """
    Select k_shot problems for few-shot prompting.
    Returns: list of (index, problem) tuples in randomized order (but consistent across runs)
    """
    n = len(problems)
    assert n > k_shot, "Not enough problems to select few-shot examples."

    # Select evenly spaced indices
    indices = [round(n * i / k_shot) for i in range(k_shot)]

    # Get problems
    few_shot = [(i, problems[i]) for i in indices]

    # Randomize order with fixed seed
    rng = random.Random(42)
    rng.shuffle(few_shot)

    return few_shot, set(indices)


def get_substitute_few_shot_index(target_index, few_shot_indices, num_problems):
    """Find a substitute index if target is in few-shot set."""
    for offset in [1, -1, 2, -2, 3, -3]:
        candidate = target_index + offset
        if 0 <= candidate < num_problems and candidate not in few_shot_indices:
            return candidate
    return None


def build_user_message(
    problem,
    repeat_problem: None | int = None,
    filler_tokens: None | int = None,
):
    """Build the user message for a problem."""
    instruction = "You will be given a question. Answer immediately using the format 'Answer: [ANSWER]' where [ANSWER] is just the answer, nothing else. No explanation, no words, no reasoning, just the answer."

    if filler_tokens is not None:
        instruction += f" After the question, there will be filler tokens (counting from 1 to {filler_tokens}) to give you extra space to process the problem before answering."

    def rep_text(idx):
        if repeat_problem is None or idx == 0:
            return ""
        return f" (repeat #{idx + 1})"

    question_text = problem.get("question", problem.get("problem", ""))

    # Build question(s) text
    num_repeats = repeat_problem if repeat_problem is not None else 1

    problem_blocks = []
    for idx in range(num_repeats):
        question_line = f"Question{rep_text(idx)}: {question_text}"
        problem_blocks.append(question_line)

    out = f"{instruction}\n\n" + "\n\n".join(problem_blocks)

    # Add filler tokens if specified
    if filler_tokens is not None:
        filler = " ".join(str(i) for i in range(1, filler_tokens + 1))
        out += f"\n\nFiller: {filler}"

    return out


def build_few_shot_messages(
    few_shot_problems,
    repeat_problem: None | int = None,
    cache: bool = False,
    filler_tokens: None | int = None,
    for_openai_chat: bool = False,
):
    """Build the few-shot messages as user/assistant pairs."""
    messages = []

    for idx, problem in few_shot_problems:
        user_text = build_user_message(
            problem,
            repeat_problem=repeat_problem,
            filler_tokens=filler_tokens,
        )
        if for_openai_chat:
            user_text += "\n\nAnswer:"

        messages.append(
            {
                "role": "user",
                "content": [{"type": "text", "text": user_text}],
            }
        )

        # Get answer - handle both string and numeric answers
        answer = problem["answer"]
        messages.append(
            {
                "role": "assistant",
                "content": f"Answer: {answer}" if not for_openai_chat else str(answer),
            }
        )

    if cache and len(few_shot_problems) > 0:
        messages[-2]["content"][0]["cache_control"] = {"type": "ephemeral"}

    return messages


def normalize_answer(answer_str: str) -> Optional[int]:
    """
    Normalize answer string for comparison.
    Remove common prefixes, strip, and try to parse as int.
    Returns None if doesn't parse as int.
    """
    answer_str = answer_str.strip().lower()

    # Remove common prefixes
    for prefix in ["answer:", "the answer is", "it is", "it's", "=", "equals"]:
        if answer_str.startswith(prefix):
            answer_str = answer_str[len(prefix):].strip()

    # Remove trailing punctuation
    answer_str = answer_str.strip(".,!?;:")

    # Remove any remaining whitespace
    answer_str = answer_str.strip()

    # Try to extract a number from the string
    # First try direct parsing
    try:
        return int(answer_str)
    except ValueError:
        pass

    # Try to find a number in the string
    match = re.search(r'^-?\d+', answer_str)
    if match:
        try:
            return int(match.group())
        except ValueError:
            pass

    return None


def check_answer(predicted: str, correct: int) -> bool:
    """Check if predicted answer matches correct answer."""
    pred_norm = normalize_answer(str(predicted))

    if pred_norm is None:
        return False

    return pred_norm == correct


async def evaluate_problem(
    problem,
    problem_index,
    semaphore,
    base_few_shot_problems,
    base_few_shot_indices,
    all_problems,
    model="claude-opus-4-5-20251101",
    repeat_problem: None | int = None,
    verbosity: int = 2,
    filler_tokens: None | int = None,
):
    """Evaluate a single problem."""
    # Determine model type
    is_openai_chat = model in OPENAI_CHAT_MODELS
    is_gemini = model in GEMINI_MODELS
    is_openrouter = model in OPENROUTER_MODELS or is_gemini

    # Check if we need to modify few-shot set
    few_shot_problems = base_few_shot_problems
    modified_few_shot = False

    if problem_index in base_few_shot_indices:
        modified_few_shot = True
        substitute_index = get_substitute_few_shot_index(problem_index, base_few_shot_indices, len(all_problems))
        if substitute_index is not None:
            few_shot_problems = [
                ((substitute_index, all_problems[substitute_index]) if idx == problem_index else (idx, prob))
                for idx, prob in base_few_shot_problems
            ]

    # Gemini supports prefill, other OpenRouter/OpenAI models don't
    disable_prefill = (is_openai_chat or is_openrouter) and not is_gemini

    # Build messages
    few_shot_messages = build_few_shot_messages(
        few_shot_problems,
        repeat_problem=repeat_problem,
        cache=not modified_few_shot and not is_openai_chat and not is_openrouter,
        filler_tokens=filler_tokens,
        for_openai_chat=disable_prefill,
    )

    max_tokens = 100

    # Build messages/cache_key based on model type
    if is_openai_chat or is_openrouter:
        # For OpenAI/OpenRouter: use chat format
        openai_messages = []
        for msg in few_shot_messages:
            content = msg["content"]
            if isinstance(content, list):
                content = content[0]["text"]
            openai_messages.append({"role": msg["role"], "content": content})
        # Add current problem
        current_user_text = build_user_message(
            problem,
            repeat_problem=repeat_problem,
            filler_tokens=filler_tokens,
        )
        if disable_prefill:
            current_user_text += "\n\nAnswer:"
            openai_messages.append({"role": "user", "content": current_user_text})
        else:
            openai_messages.append({"role": "user", "content": current_user_text})
            openai_messages.append({"role": "assistant", "content": "Answer:"})
        if is_gemini:
            cache_key = {
                "model": model,
                "max_completion_tokens": 20,
                "messages": openai_messages,
                "temperature": 0.0,
                "extra_body": {
                    "reasoning": {
                        "enabled": True,
                        "thinking_level": "low",
                        "max_tokens": 10,
                    }
                },
            }
        elif "gpt-5" in model:
            cache_key = {
                "model": model,
                "max_completion_tokens": max_tokens,
                "messages": openai_messages,
                "reasoning_effort": "none",
            }
        else:
            cache_key = {"model": model, "max_tokens": max_tokens, "messages": openai_messages}
    else:
        # For Anthropic: use original format with prefill
        messages = few_shot_messages + [
            {
                "role": "user",
                "content": build_user_message(
                    problem,
                    repeat_problem=repeat_problem,
                    filler_tokens=filler_tokens,
                ),
            },
            {"role": "assistant", "content": "Answer:"},
        ]
        cache_key = {"model": model, "max_tokens": max_tokens, "messages": messages}

    # Check cache
    cached_response = await response_cache.get(cache_key)

    async with semaphore:
        try:
            response_text = ""

            if cached_response:
                if verbosity >= 3:
                    print(f"[CACHED] Problem {problem_index + 1}")
                response_text = cached_response.get("response", "")
            else:
                if verbosity >= 2:
                    print(f"Starting problem {problem_index + 1}: {problem.get('type', 'unknown')}")

                max_retries = 8
                for retry in range(max_retries):
                    try:
                        if is_openrouter:
                            # OpenRouter API
                            if is_gemini:
                                gemini_max_retries = 5
                                for gemini_retry in range(gemini_max_retries):
                                    response = await asyncio.wait_for(
                                        openrouter_client.chat.completions.create(
                                            **cache_key,
                                        ),
                                        timeout=120.0,
                                    )
                                    assert response.choices is not None
                                    choice = response.choices[0]
                                    assert choice is not None
                                    response_text = choice.message.content.strip()
                                    thinking = None
                                    if hasattr(choice.message, "reasoning") and choice.message.reasoning:
                                        thinking = choice.message.reasoning
                                    elif hasattr(choice.message, "reasoning_content") and choice.message.reasoning_content:
                                        thinking = choice.message.reasoning_content

                                    if thinking is not None:
                                        response_text = "INVALID WAS THINKING"
                                        if verbosity >= 2:
                                            print(f"  Gemini model {model} returned reasoning, retrying ({gemini_retry + 1}/{gemini_max_retries}). Thinking: {thinking[:100]}")
                                    elif response_text == "":
                                        if verbosity >= 2:
                                            print(f"  Gemini returned empty response, retrying ({gemini_retry + 1}/{gemini_max_retries})...")
                                    else:
                                        assert thinking is None and response_text != ""
                                        if verbosity >= 2 and gemini_retry > 0:
                                            print(f"  Gemini succeeded on retry {gemini_retry + 1}")
                                        break
                                else:
                                    if verbosity >= 2:
                                        print(f"  Gemini returned empty/thinking response after {gemini_max_retries} retries")
                            else:
                                response = await asyncio.wait_for(
                                    openrouter_client.chat.completions.create(
                                        **cache_key,
                                        temperature=0.0,
                                    ),
                                    timeout=120.0,
                                )
                                response_text = response.choices[0].message.content.strip()
                        elif is_openai_chat:
                            # OpenAI chat API
                            response = await asyncio.wait_for(
                                openai_client.chat.completions.create(
                                    **cache_key,
                                    temperature=0.0,
                                ),
                                timeout=120.0,
                            )
                            response_text = response.choices[0].message.content.strip()
                        else:
                            # Anthropic API
                            response = await asyncio.wait_for(
                                anthropic_client.messages.create(
                                    model=model,
                                    max_tokens=max_tokens,
                                    messages=messages,
                                    timeout=60.0,
                                    temperature=0.0,
                                ),
                                timeout=120.0,
                            )

                            # Track costs (Anthropic only)
                            if hasattr(response, "usage"):
                                COST_TRACKER["input_tokens"] += response.usage.input_tokens
                                COST_TRACKER["output_tokens"] += response.usage.output_tokens
                                if hasattr(response.usage, "cache_read_input_tokens"):
                                    COST_TRACKER["cache_read_tokens"] += response.usage.cache_read_input_tokens or 0
                                if hasattr(response.usage, "cache_creation_input_tokens"):
                                    COST_TRACKER["cache_creation_tokens"] += response.usage.cache_creation_input_tokens or 0

                            for block in response.content:
                                if block.type == "text":
                                    response_text = block.text

                        # Cache response
                        await response_cache.set(cache_key, {"response": response_text})
                        break  # Success, exit retry loop

                    except asyncio.TimeoutError:
                        if retry < max_retries - 1:
                            print(f"TIMEOUT on problem {problem_index + 1}, retrying ({retry + 1}/{max_retries})...")
                            await asyncio.sleep(5 * (retry + 1))
                        else:
                            print(f"TIMEOUT on problem {problem_index + 1} after {max_retries} retries")
                            raise Exception("API call timed out after retries")

                    except Exception as e:
                        if "rate_limit" in str(e).lower() or "429" in str(e):
                            if retry < max_retries - 1:
                                wait_time = 0.1 * (2**retry)
                                print(
                                    f"Rate limited on problem {problem_index + 1}, waiting {wait_time}s ({retry + 1}/{max_retries})..."
                                )
                                await asyncio.sleep(wait_time)
                            else:
                                raise
                        else:
                            raise

            # Check answer
            correct_answer = problem["answer"]
            is_correct = check_answer(response_text, correct_answer)

            result = {
                "problem_index": problem_index,
                "type": problem.get("type", "unknown"),
                "num_addends": problem.get("num_addends", "unknown"),
                "question": problem.get("question", problem.get("problem", "")),
                "correct_answer": correct_answer,
                "predicted_answer": response_text.strip(),
                "is_correct": is_correct,
                "response": response_text,
                "cached": cached_response is not None,
                "chain": problem.get("chain", []),
            }

            status = "CORRECT" if is_correct else "INCORRECT"
            cache_status = "[CACHED]" if cached_response else ""
            if verbosity >= 3:
                print(
                    f"Problem {problem_index + 1}: {status} ('{response_text.strip()}' vs '{correct_answer}') {cache_status}"
                )

            return result

        except Exception as e:
            import traceback

            error_msg = str(e)
            print(f"Error on problem {problem_index + 1}: {error_msg}")
            return {
                "problem_index": problem_index,
                "type": problem.get("type", "unknown"),
                "num_addends": problem.get("num_addends", "unknown"),
                "question": problem.get("question", problem.get("problem", "")),
                "correct_answer": problem["answer"],
                "predicted_answer": None,
                "is_correct": False,
                "error": error_msg,
                "cached": False,
            }


async def run_evaluation(
    input_file,
    output_file=None,
    max_problems=None,
    concurrency=40,
    model="claude-opus-4-5-20251101",
    repeat_problem: None | int = None,
    verbosity: int = 2,
    k_shot: int = 10,
    randomize_n: bool = False,
    seed_for_n: int = 42,
    addend_filter: int | None = None,
    filler_tokens: None | int = None,
):
    """Run evaluation on all problems."""
    all_problems = load_problems(input_file)

    # Select few-shot examples from ALL problems (before any filtering)
    few_shot_problems, few_shot_indices = select_few_shot_problems(all_problems, k_shot=k_shot)

    # Filter by addend count if specified (after selecting few-shot)
    if addend_filter is not None:
        original_count = len(all_problems)
        problems_with_indices = [
            (i, p) for i, p in enumerate(all_problems)
            if p.get("num_addends") == addend_filter
        ]
        if verbosity >= 1:
            print(f"Filtered to {len(problems_with_indices)} problems with {addend_filter} addends (from {original_count} total)")
    else:
        problems_with_indices = [(i, p) for i, p in enumerate(all_problems)]

    if verbosity >= 2:
        print(f"\nFew-shot examples:")
        for idx, prob in few_shot_problems:
            q = prob.get("question", prob.get("problem", ""))[:60]
            print(f"  - Problem {idx}: {q}... -> {prob['answer']}")

    print(f"{len(few_shot_problems)=}")

    # Determine problems to evaluate
    if max_problems:
        available = [(idx, p) for idx, p in problems_with_indices if idx not in few_shot_indices]
        if randomize_n:
            rng = random.Random(seed_for_n)
            rng.shuffle(available)
        problems_to_eval = available[:max_problems]
    else:
        problems_to_eval = [(idx, p) for idx, p in problems_with_indices if idx not in few_shot_indices]

    if verbosity >= 1:
        print(f"\nEvaluating {len(problems_to_eval)} problems with concurrency={concurrency}...")
        if randomize_n and max_problems:
            print(f"  Randomized selection (seed={seed_for_n})")
        if filler_tokens:
            print(f"  Filler tokens: {filler_tokens}")

    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        evaluate_problem(
            problem,
            problem_idx,
            semaphore,
            few_shot_problems,
            few_shot_indices,
            all_problems,
            model,
            repeat_problem=repeat_problem,
            verbosity=verbosity,
            filler_tokens=filler_tokens,
        )
        for problem_idx, problem in problems_to_eval
    ]

    results = await asyncio.gather(*tasks)

    # Save cache
    await response_cache.save_cache(force=True)

    # Sort by index
    results = sorted(results, key=lambda x: x["problem_index"])

    # Calculate statistics
    correct_count = sum(1 for r in results if r["is_correct"])
    cached_count = sum(1 for r in results if r.get("cached", False))
    accuracy = correct_count / len(results) if results else 0

    # Calculate by number of addends
    addend_stats = {}
    for r in results:
        num_addends = r.get("num_addends", "unknown")
        if num_addends not in addend_stats:
            addend_stats[num_addends] = {"total": 0, "correct": 0}
        addend_stats[num_addends]["total"] += 1
        if r["is_correct"]:
            addend_stats[num_addends]["correct"] += 1

    if verbosity >= 1:
        print(f"\n{'='*60}")
        print(f"EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total problems: {len(results)}")
        print(f"Correct: {correct_count}")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Cache hits: {cached_count}/{len(results)}")
        if model in GEMINI_MODELS:
            gemini_thinking_count = sum(1 for r in results if r.get("response") == "INVALID WAS THINKING")
            gemini_empty_count = sum(1 for r in results if r.get("response") == "")
            if gemini_thinking_count > 0 or gemini_empty_count > 0:
                print(f"Gemini failures: {gemini_thinking_count} thinking, {gemini_empty_count} empty")
        print(f"\nBy number of addends:")
        for num_addends, stats in sorted(addend_stats.items(), key=lambda x: (isinstance(x[0], str), x[0])):
            addend_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {num_addends} addends: {stats['correct']}/{stats['total']} ({addend_acc:.2%})")

        # Print cost estimate
        if model in PRICING:
            pricing = PRICING[model]
            cost = (
                COST_TRACKER["input_tokens"] * pricing["input"] / 1_000_000
                + COST_TRACKER["output_tokens"] * pricing["output"] / 1_000_000
                + COST_TRACKER["cache_read_tokens"] * pricing["cache_read"] / 1_000_000
                + COST_TRACKER["cache_creation_tokens"] * pricing["cache_write"] / 1_000_000
            )
            print(f"\nEstimated cost: ${cost:.4f}")
            print(f"  Input tokens: {COST_TRACKER['input_tokens']:,}")
            print(f"  Output tokens: {COST_TRACKER['output_tokens']:,}")
            print(f"  Cache read tokens: {COST_TRACKER['cache_read_tokens']:,}")
            print(f"  Cache creation tokens: {COST_TRACKER['cache_creation_tokens']:,}")

    # Save results
    if output_file:
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "model": model,
                        "total": len(results),
                        "correct": correct_count,
                        "accuracy": accuracy,
                        "repeat_problem": repeat_problem,
                        "k_shot": k_shot,
                        "randomize_n": randomize_n,
                        "seed_for_n": seed_for_n if randomize_n else None,
                        "addend_filter": addend_filter,
                        "filler_tokens": filler_tokens,
                        "addend_stats": {str(k): v for k, v in addend_stats.items()},
                        "cost_tracker": COST_TRACKER,
                    },
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        if verbosity >= 1:
            print(f"\nResults saved to: {output_file}")

    return results


def parse_model_name(model_shorthand):
    """Convert model shorthand to full model ID."""
    model_map = {
        # Anthropic models
        "opus-4-5": "claude-opus-4-5-20251101",
        "opus-4": "claude-opus-4-20250514",
        "sonnet-4": "claude-sonnet-4-20250514",
        "sonnet-4-5": "claude-sonnet-4-5-20250929",
        "haiku-3-5": "claude-3-5-haiku-20241022",
        # OpenAI models
        "gpt-3.5": "gpt-3.5-turbo-0125",
        "gpt-4": "gpt-4-0314",
        "gpt-4o": "gpt-4o-2024-05-13",
        "gpt-4.1": "gpt-4.1-2025-04-14",
        "gpt-5.1": "gpt-5.1-2025-11-13",
        "gpt-5.2": "gpt-5.2-2025-12-11",
        # OpenRouter models
        "deepseek-v3": "deepseek/deepseek-chat-v3-0324",
        "deepseek-v3.2": "deepseek/deepseek-v3.2",
        "qwen3-235b": "qwen/qwen3-235b-a22b-2507",
        "qwen3-480b": "qwen/qwen3-coder",
        "qwen3-32b": "qwen/qwen3-32b",
        "kimi-k2": "moonshotai/kimi-k2",
        # Gemini models
        "gemini-2.5-pro": "google/gemini-2.5-pro",
        "gemini-3-pro": "google/gemini-3-pro-preview",
    }
    return model_map.get(model_shorthand, model_shorthand)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate addition problems without CoT")
    parser.add_argument("--num-problems", "-n", type=int, default=None,
                        help="Maximum number of problems to evaluate")
    parser.add_argument("--concurrency", "-c", type=int, default=40)
    parser.add_argument("--model", "-m", type=str, default="opus-4-5")
    parser.add_argument("--input", "-i", type=str, default="data/addition_problems.jsonl")
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--repeat-problem", "-r", type=int, default=None)
    parser.add_argument("--verbosity", "-v", type=int, default=2)
    parser.add_argument("--k-shot", "-k", type=int, default=10)
    parser.add_argument("--randomize-n", action="store_true",
                        help="Randomly select problems when using -n (instead of first n)")
    parser.add_argument("--seed-for-n", type=int, default=42,
                        help="Random seed for problem selection when using --randomize-n (default: 42)")
    parser.add_argument("--addends", type=int, default=None,
                        help="Only evaluate problems with this many addends (e.g., --addends 4)")
    parser.add_argument("--filler-tokens", "-f", type=int, default=None,
                        help="Number of filler tokens (counting 1 to N) to add after the problem")

    args = parser.parse_args()

    model = parse_model_name(args.model)

    # Auto-generate output filename if not specified
    if args.output is None:
        repeat_suffix = f"_r{args.repeat_problem}" if args.repeat_problem else ""
        addend_suffix = f"_{args.addends}add" if args.addends else ""
        n_suffix = f"_n{args.num_problems}" if args.num_problems else ""
        rand_suffix = f"_rand{args.seed_for_n}" if args.randomize_n and args.num_problems else ""
        filler_suffix = f"_f{args.filler_tokens}" if args.filler_tokens else ""
        args.output = f"eval_results/addition_eval_{args.model}{addend_suffix}{n_suffix}{rand_suffix}{repeat_suffix}{filler_suffix}.json"

    if args.verbosity >= 1:
        print(f"Configuration:")
        print(f"  Model: {model}")
        print(f"  Concurrency: {args.concurrency}")
        print(f"  Max problems: {args.num_problems if args.num_problems else 'all'}")
        if args.randomize_n and args.num_problems:
            print(f"  Randomize selection: True (seed={args.seed_for_n})")
        if args.addends:
            print(f"  Addend filter: {args.addends} addends only")
        print(f"  Repeat problem: {args.repeat_problem}")
        print(f"  K-shot: {args.k_shot}")
        if args.filler_tokens:
            print(f"  Filler tokens: {args.filler_tokens}")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output}")

    asyncio.run(
        run_evaluation(
            args.input,
            args.output,
            args.num_problems,
            args.concurrency,
            model,
            repeat_problem=args.repeat_problem,
            verbosity=args.verbosity,
            k_shot=args.k_shot,
            randomize_n=args.randomize_n,
            seed_for_n=args.seed_for_n,
            addend_filter=args.addends,
            filler_tokens=args.filler_tokens,
        )
    )

#!/usr/bin/env python3
"""
Evaluation script for multi-hop reasoning problems using Claude WITHOUT reasoning (few-shot).
"""

import json
import re
import os
import asyncio
import random
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from response_cache import ResponseCache
from unidecode import unidecode
from generate_dataset import US_STATE_MOTTOS, US_STATE_FLOWERS
from generate_dataset_constants import MAPPING_REGISTRY

# Load API key
if "ANTHROPIC_API_KEY" not in os.environ:
    key_path = os.path.expanduser("~/.anthropic_api_key")
    try:
        with open(key_path, "r") as f:
            os.environ["ANTHROPIC_API_KEY"] = f.read().strip()
    except FileNotFoundError:
        print("Warning: No API key found at ~/.anthropic_api_key")

# Initialize client
anthropic_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Initialize cache
response_cache = ResponseCache("caches/cache_multi_hop.json")

# Cost tracking
COST_TRACKER = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_creation_tokens": 0,
}

# Pricing per million tokens (as of late 2024/2025)
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


def format_mapping_as_table(mapping_id: str, table_num: int) -> str:
    """
    Format a mapping as a key-value list table.
    Returns a string like:
    === Table 1: Element Name to Atomic Number ===
    Hydrogen: 1
    Helium: 2
    ...
    """
    if mapping_id not in MAPPING_REGISTRY:
        return f"=== Table {table_num}: Unknown mapping '{mapping_id}' ==="

    mapping_info = MAPPING_REGISTRY[mapping_id]
    data = mapping_info["data"]
    title = mapping_info["title"]

    lines = [f"=== Table {table_num}: {title} ==="]
    for key, value in data.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def get_problem_mappings(problem: Dict[str, Any]) -> List[str]:
    """
    Extract all unique mapping_ids from a problem's chain.
    Returns list of mapping_ids in order they appear in the chain.
    """
    mapping_ids = []
    chain = problem.get("chain", [])
    for step in chain:
        mapping_id = step.get("mapping_id")
        if mapping_id and mapping_id not in mapping_ids:
            mapping_ids.append(mapping_id)
    return mapping_ids


def build_mapping_tables_text(problem: Dict[str, Any]) -> str:
    """
    Build the full text of all mapping tables for a problem.
    Each step in the chain gets its own table instance (even if same mapping type).
    """
    chain = problem.get("chain", [])
    tables = []
    table_num = 1

    for step in chain:
        mapping_id = step.get("mapping_id")
        if mapping_id:
            table_text = format_mapping_as_table(mapping_id, table_num)
            tables.append(table_text)
            table_num += 1

    return "\n\n".join(tables)


def build_user_message(
    problem,
    repeat_problem: None | int = None,
    include_mappings: bool = False,
    mapping_position: str = "before",
    filler_tokens: None | int = None,
):
    """Build the user message for a problem.

    Args:
        problem: The problem dict containing question and chain
        repeat_problem: Number of times to repeat the problem (None = 1 time)
        include_mappings: Whether to include mapping tables in context
        mapping_position: Where to place tables - "before" or "after" the question
        filler_tokens: Number of filler tokens (counting 1 to N) to add after the problem
    """
    instruction = "You will be given a question. Answer immediately using the format 'Answer: [ANSWER]' where [ANSWER] is just the answer, nothing else. No explanation, no words, no reasoning, just the answer."

    if filler_tokens is not None:
        instruction += f" After the question, there will be filler tokens (counting from 1 to {filler_tokens}) to give you extra space to process the problem before answering."

    def rep_text(idx):
        if repeat_problem is None or idx == 0:
            return ""
        return f" (repeat #{idx + 1})"

    question_text = problem.get("question", problem.get("problem", ""))

    # Build the mapping tables text if needed
    tables_text = ""
    if include_mappings:
        tables_text = build_mapping_tables_text(problem)

    # Build question(s) text
    num_repeats = repeat_problem if repeat_problem is not None else 1

    # Build the problem block (tables + question or question + tables)
    problem_blocks = []
    for idx in range(num_repeats):
        question_line = f"Question{rep_text(idx)}: {question_text}"

        if include_mappings and tables_text:
            if mapping_position == "before":
                block = f"{tables_text}\n\n{question_line}"
            else:  # "after"
                block = f"{question_line}\n\n{tables_text}"
        else:
            block = question_line

        problem_blocks.append(block)

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
    include_mappings: bool = False,
    mapping_position: str = "before",
    filler_tokens: None | int = None,
):
    """Build the few-shot messages as user/assistant pairs."""
    messages = []

    for idx, problem in few_shot_problems:
        user_text = build_user_message(
            problem,
            repeat_problem=repeat_problem,
            include_mappings=include_mappings,
            mapping_position=mapping_position,
            filler_tokens=filler_tokens,
        )

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
                "content": f"Answer: {answer}",
            }
        )

    if cache and len(few_shot_problems) > 0:
        messages[-2]["content"][0]["cache_control"] = {"type": "ephemeral"}

    return messages


def remove_middle_names(name_str: str) -> str:
    """
    Remove middle names from a person's name (conservative approach).
    Only applied to names with 3+ words where all words are alphabetic.
    Preserves suffixes like Jr., Sr., I, II, III.
    """
    words = name_str.split()
    if len(words) < 3:
        return name_str
    if len(words) > 4:
        return name_str

    # Only apply to names that look like person names (all words are alphabetic)
    # Allow apostrophes and hyphens which are common in names
    if not all(word.replace("'", "").replace("-", "").isalpha() for word in words):
        return name_str

    # Preserve common suffixes
    suffixes = {"jr", "sr", "i", "ii", "iii", "iv", "v"}
    if words[-1] in suffixes and len(words) in [3, 4]:
        if len(words) == 4:
            return f"{words[0]} {words[-2]} {words[-1]}"
        else:
            # Only 3 words with suffix (e.g., "John Smith Jr"), don't modify
            return name_str
    if len(words) > 3:
        return name_str

    if len(words) == 3:
        return f"{words[0]} {words[2]}"

    raise ValueError("shoudn't be reachable")


def normalize_answer(answer_str: str, skip_middle_name_normalization: bool = False) -> str:
    """Normalize answer string for comparison."""
    answer_str = answer_str.strip().lower()
    answer_str = unidecode(answer_str)

    # Remove common prefixes
    for prefix in ["answer:", "the answer is", "it is", "it's"]:
        if answer_str.startswith(prefix):
            answer_str = answer_str[len(prefix) :].strip()

    answer_str = answer_str.replace("t.s.", "t. s.")
    answer_str = answer_str.replace("j.j.", "j. j.")
    answer_str = answer_str.removeprefix("mr. ").strip()
    answer_str = answer_str.removeprefix("sir. ").strip()
    answer_str = answer_str.removeprefix("mr ").strip()
    answer_str = answer_str.removeprefix("sir ").strip()
    answer_str = answer_str.removeprefix("lord ").strip()

    # Remove parenthetical explanations (e.g., "Cardinal (Northern Cardinal)" -> "Cardinal")
    answer_str = re.sub(r"\s*\([^)]*\)", "", answer_str).strip()

    answer_str = answer_str.replace("robert bruce merrifield", "bruce merrifield").strip()
    answer_str = answer_str.replace("oscar arias sanchez", "oscar arias").strip()
    answer_str = answer_str.replace("john boyd orr", "boyd orr").strip()
    answer_str = answer_str.replace("hermann emil fischer", "emil fischer").strip()
    answer_str = answer_str.replace("petrus debye", "peter debye").strip()
    answer_str = answer_str.replace("adolf otto reinhold windaus", "adolf windaus").strip()
    answer_str = answer_str.replace("william randal cremer", "randal cremer").strip()
    answer_str = answer_str.replace("rigoberta menchu tum", "rigoberta menchu").strip()

    answer_str = answer_str.replace("fatti maschi,", "fatti maschii,").strip()

    answer_str = answer_str.replace("washington, d.c.", "district of columbia").strip()
    answer_str = answer_str.replace("d.c.", "district of columbia").strip()

    answer_str = answer_str.replace("audemus jura nostra defendere", "we dare defend our rights").strip()
    answer_str = answer_str.replace("and ", "").strip()

    answer_str = answer_str.replace("-", "").strip()
    answer_str = answer_str.replace(",", "").strip()
    answer_str = answer_str.replace(".", "").strip()
    answer_str = answer_str.replace("'", "").strip()  # Remove apostrophes
    answer_str = answer_str.replace("`", "").strip()  # Remove backticks (Hawaiian ʻokina after unidecode)

    # some overkill here
    answer_str = answer_str.strip(".,!?;:").strip()
    answer_str = answer_str.removeprefix("the ").strip()
    answer_str = answer_str.removeprefix("[").removesuffix("]").strip()
    answer_str = answer_str.strip(".,!?;:").strip()
    answer_str = answer_str.removeprefix("the ").strip()

    answer_str = answer_str.removeprefix("northern").strip()
    answer_str = answer_str.removeprefix("western").strip()
    answer_str = answer_str.removeprefix("eastern").strip()
    answer_str = answer_str.removeprefix("southern").strip()
    answer_str = answer_str.removeprefix("american").strip()
    answer_str = answer_str.replace("hawaiian hibiscus", "hibiscus")
    answer_str = answer_str.replace("white hawthorn blossom", "hawthorn")
    answer_str = answer_str.replace("common meadow violet", "violet")
    answer_str = answer_str.replace("yucca flower", "yucca")

    if (not skip_middle_name_normalization) and (answer_str not in NORMALIZED_NON_NAME_SET):
        # Remove middle names from person names (conservative, only affects 3+ word names)
        answer_str = remove_middle_names(answer_str)

    return answer_str


NORMALIZED_NON_NAME_SET = set(
    normalize_answer(x, skip_middle_name_normalization=True)
    for x in [*US_STATE_MOTTOS.values(), *US_STATE_FLOWERS.values()]
)


def check_answer(predicted: str, correct) -> bool:
    """Check if predicted answer matches correct answer."""
    pred_norm = normalize_answer(str(predicted))
    correct_norm = normalize_answer(str(correct))

    # Direct match (includes middle name removal since it's in normalize_answer)
    if pred_norm == correct_norm:
        return True

    # For numeric answers, try parsing
    try:
        pred_num = int(pred_norm)
        correct_num = int(correct)
        if pred_num == correct_num:
            return True
    except ValueError:
        pass

    return False

    # # Check if correct answer is contained in prediction (for names)
    # if correct_norm in pred_norm:
    #     return True

    # # Check if prediction is contained in correct (handles partial matches)
    # if pred_norm in correct_norm and len(pred_norm) > 3:
    #     return True

    # return False


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
    include_mappings: bool = False,
    mapping_position: str = "before",
    filler_tokens: None | int = None,
):
    """Evaluate a single problem."""
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

    # Build messages
    few_shot_messages = build_few_shot_messages(
        few_shot_problems,
        repeat_problem=repeat_problem,
        cache=not modified_few_shot,
        include_mappings=include_mappings,
        mapping_position=mapping_position,
        filler_tokens=filler_tokens,
    )

    max_tokens = 100

    messages = few_shot_messages + [
        {
            "role": "user",
            "content": build_user_message(
                problem,
                repeat_problem=repeat_problem,
                include_mappings=include_mappings,
                mapping_position=mapping_position,
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

                        # Track costs
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
                "hops": problem.get("hops", problem.get("fact_type", "unknown")),
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
                "hops": problem.get("hops", "unknown"),
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
    include_mappings: bool = False,
    mapping_position: str = "before",
    randomize_n: bool = False,
    seed_for_n: int = 42,
    hop_filter: int | None = None,
    filler_tokens: None | int = None,
):
    """Run evaluation on all problems."""
    all_problems = load_problems(input_file)

    # Select few-shot examples from ALL problems (before any filtering)
    few_shot_problems, few_shot_indices = select_few_shot_problems(all_problems, k_shot=k_shot)

    # Filter by hop count if specified (after selecting few-shot)
    if hop_filter is not None:
        original_count = len(all_problems)
        # Create list of (original_index, problem) for filtered problems
        problems_with_indices = [
            (i, p) for i, p in enumerate(all_problems)
            if p.get("hops") == hop_filter
        ]
        if verbosity >= 1:
            print(f"Filtered to {len(problems_with_indices)} problems with {hop_filter} hops (from {original_count} total)")
    else:
        problems_with_indices = [(i, p) for i, p in enumerate(all_problems)]

    if verbosity >= 2:
        print(f"\nFew-shot examples:")
        for idx, prob in few_shot_problems:
            q = prob.get("question", prob.get("problem", ""))[:60]
            print(f"  - Problem {idx}: {q}... -> {prob['answer']}")

    # Determine problems to evaluate (from the filtered set)
    # problems_with_indices is a list of (original_index, problem) tuples
    if max_problems:
        available = [(idx, p) for idx, p in problems_with_indices if idx not in few_shot_indices]
        if randomize_n:
            # Randomly select max_problems, excluding few-shot examples
            rng = random.Random(seed_for_n)
            rng.shuffle(available)
        problems_to_eval = available[:max_problems]
    else:
        # Exclude few-shot from evaluation
        problems_to_eval = [(idx, p) for idx, p in problems_with_indices if idx not in few_shot_indices]

    if verbosity >= 1:
        print(f"\nEvaluating {len(problems_to_eval)} problems with concurrency={concurrency}...")
        if include_mappings:
            print(f"  Including mapping tables (position: {mapping_position})")
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
            include_mappings=include_mappings,
            mapping_position=mapping_position,
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

    # Calculate by hop level
    hop_stats = {}
    for r in results:
        hop = r.get("hops", "unknown")
        if hop not in hop_stats:
            hop_stats[hop] = {"total": 0, "correct": 0}
        hop_stats[hop]["total"] += 1
        if r["is_correct"]:
            hop_stats[hop]["correct"] += 1

    if verbosity >= 1:
        print(f"\n{'='*60}")
        print(f"EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total problems: {len(results)}")
        print(f"Correct: {correct_count}")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Cache hits: {cached_count}/{len(results)}")
        print(f"\nBy hop level:")
        for hop, stats in sorted(hop_stats.items(), key=lambda x: str(x[0])):
            hop_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {hop}-hop: {stats['correct']}/{stats['total']} ({hop_acc:.2%})")

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
                        "include_mappings": include_mappings,
                        "mapping_position": mapping_position if include_mappings else None,
                        "randomize_n": randomize_n,
                        "seed_for_n": seed_for_n if randomize_n else None,
                        "hop_filter": hop_filter,
                        "filler_tokens": filler_tokens,
                        "hop_stats": {str(k): v for k, v in hop_stats.items()},
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
        "opus-4-5": "claude-opus-4-5-20251101",
        "opus-4": "claude-opus-4-20250514",
        "sonnet-4": "claude-sonnet-4-20250514",
        "sonnet-4-5": "claude-sonnet-4-5-20250929",
        "haiku-3-5": "claude-3-5-haiku-20241022",
    }
    return model_map.get(model_shorthand, model_shorthand)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate multi-hop reasoning without CoT")
    parser.add_argument("--num-problems", "-n", type=int, default=None,
                        help="Maximum number of problems to evaluate")
    parser.add_argument("--concurrency", "-c", type=int, default=40)
    parser.add_argument("--model", "-m", type=str, default="opus-4-5")
    parser.add_argument("--input", "-i", type=str, default="data/problems_all.jsonl")
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--repeat-problem", "-r", type=int, default=None)
    parser.add_argument("--verbosity", "-v", type=int, default=2)
    parser.add_argument("--k-shot", "-k", type=int, default=10)
    parser.add_argument("--only-salient-facts", action="store_true",
                        help="Use salient facts dataset (changes input/output paths)")
    parser.add_argument("--include-mappings", action="store_true",
                        help="Include mapping tables in the prompt context")
    parser.add_argument("--mapping-position", type=str, default="before", choices=["before", "after"],
                        help="Position of mapping tables relative to question (default: before)")
    parser.add_argument("--randomize-n", action="store_true",
                        help="Randomly select problems when using -n (instead of first n)")
    parser.add_argument("--seed-for-n", type=int, default=42,
                        help="Random seed for problem selection when using --randomize-n (default: 42)")
    parser.add_argument("--hop", type=int, default=None,
                        help="Only evaluate problems with this many hops (e.g., --hop 4)")
    parser.add_argument("--filler-tokens", "-f", type=int, default=None,
                        help="Number of filler tokens (counting 1 to N) to add after the problem")

    args = parser.parse_args()

    model = parse_model_name(args.model)

    # Handle --only-salient-facts flag
    if args.only_salient_facts:
        if args.input != "data/problems_all.jsonl":
            print(f"Warning: --only-salient-facts overrides --input. Ignoring: {args.input}")
        args.input = "data/salient_problems_all.jsonl"

    # Auto-generate output filename if not specified
    output_prefix = "eval_results/salient_" if args.only_salient_facts else "eval_results/"
    if args.output is None:
        repeat_suffix = f"_r{args.repeat_problem}" if args.repeat_problem else ""
        mapping_suffix = f"_map{args.mapping_position[0]}" if args.include_mappings else ""
        hop_suffix = f"_{args.hop}hop" if args.hop else ""
        n_suffix = f"_n{args.num_problems}" if args.num_problems else ""
        rand_suffix = f"_rand{args.seed_for_n}" if args.randomize_n and args.num_problems else ""
        filler_suffix = f"_f{args.filler_tokens}" if args.filler_tokens else ""
        args.output = f"{output_prefix}eval_{args.model}{hop_suffix}{n_suffix}{rand_suffix}{repeat_suffix}{filler_suffix}{mapping_suffix}.json"

    if args.verbosity >= 1:
        print(f"Configuration:")
        print(f"  Model: {model}")
        print(f"  Concurrency: {args.concurrency}")
        print(f"  Max problems: {args.num_problems if args.num_problems else 'all'}")
        if args.randomize_n and args.num_problems:
            print(f"  Randomize selection: True (seed={args.seed_for_n})")
        if args.hop:
            print(f"  Hop filter: {args.hop}-hop only")
        print(f"  Repeat problem: {args.repeat_problem}")
        print(f"  K-shot: {args.k_shot}")
        print(f"  Include mappings: {args.include_mappings}")
        if args.include_mappings:
            print(f"  Mapping position: {args.mapping_position}")
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
            include_mappings=args.include_mappings,
            mapping_position=args.mapping_position,
            randomize_n=args.randomize_n,
            seed_for_n=args.seed_for_n,
            hop_filter=args.hop,
            filler_tokens=args.filler_tokens,
        )
    )

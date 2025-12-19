#!/usr/bin/env python3
"""
Verify that Opus 4.5 can correctly answer multi-hop reasoning questions with extended thinking enabled.

This validates that the model can solve the full multi-hop chains when allowed to think.
"""

import json
import asyncio
import re
import sys
from pathlib import Path
from collections import defaultdict
from anthropic import AsyncAnthropic
import os
from eval_multi_hop import check_answer
from response_cache import ResponseCache


def extract_boxed_answer(text):
    """Extract the answer from \\boxed{...} format."""
    # Look for \boxed{...} pattern
    match = re.search(r'\\boxed\{([^}]+)\}', text)
    if match:
        return match.group(1).strip()
    # Fallback: return the whole text stripped
    return text.strip()

# Get API key
api_key_file = Path.home() / ".anthropic_api_key"
if api_key_file.exists():
    ANTHROPIC_API_KEY = api_key_file.read_text().strip()
else:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-opus-4-20250514"

# Initialize cache
cache = ResponseCache("caches/multihop_thinking_cache.json", save_every=50)


async def ask_multihop_question_with_thinking(problem, semaphore):
    """Ask Opus 4 a multi-hop question with extended thinking enabled."""
    prompt = f"""You will be given a question. Put your final answer in \\boxed{{}}. For example: \\boxed{{42}} or \\boxed{{Abraham Lincoln}}

Question: {problem['question']}"""

    messages = [
        {"role": "user", "content": prompt},
    ]

    # Create cache key based on messages to ensure prompt changes don't hit stale cache
    cache_key = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 16000,
        "thinking": {
            "type": "enabled",
            "budget_tokens": 10000,
        },
    }

    # Check cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        raw_response = cached["response"]
        predicted = extract_boxed_answer(raw_response)
        is_correct = check_answer(predicted, problem["answer"])
        return {
            "question": problem["question"],
            "correct_answer": problem["answer"],
            "predicted": predicted,
            "is_correct": is_correct,
            "type": problem["type"],
            "hops": problem["hops"],
            "cached": True,
        }

    async with semaphore:
        max_retries = 8
        for retry in range(max_retries):
            try:
                response = await anthropic_client.messages.create(
                    model=MODEL,
                    max_tokens=16000,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 10000,
                    },
                    messages=messages
                )

                # Extract the text response (skip thinking blocks)
                predicted = ""
                for block in response.content:
                    if block.type == "text":
                        predicted = block.text.strip()
                        break

                # Cache the response
                await cache.set(cache_key, {"response": predicted})

                # Extract answer from \boxed{} format
                predicted = extract_boxed_answer(predicted)

                is_correct = check_answer(predicted, problem["answer"])

                return {
                    "question": problem["question"],
                    "correct_answer": problem["answer"],
                    "predicted": predicted,
                    "is_correct": is_correct,
                    "type": problem["type"],
                    "hops": problem["hops"],
                    "cached": False,
                }
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    wait_time = 0.1 * (2**retry)
                    print(f"Rate limit hit, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Error: {e}")
                    return None

        return None


def load_problems(filepath):
    """Load problems from JSONL file."""
    problems = []
    with open(filepath, "r") as f:
        for line in f:
            problems.append(json.loads(line))
    return problems


async def evaluate_multihop(problems, max_per_hop=50):
    """Evaluate Opus 4.5 on multi-hop questions with thinking."""
    print("="*80)
    print("MULTI-HOP REASONING WITH EXTENDED THINKING")
    print("="*80)
    print(f"Model: {MODEL}")
    print(f"Thinking enabled: budget_tokens=10000")
    print()

    # Group problems by hop count
    problems_by_hop = defaultdict(list)
    for p in problems:
        problems_by_hop[p["hops"]].append(p)

    # Summary of what we're testing
    for hops in sorted(problems_by_hop.keys()):
        print(f"{hops}-hop: {len(problems_by_hop[hops])} total problems")
    print()

    # Run evaluations
    semaphore = asyncio.Semaphore(100)  # Limit concurrency

    results_by_hop = {}

    for hops in sorted(problems_by_hop.keys()):
        print(f"\nTesting {hops}-hop problems...")

        # Sample up to max_per_hop problems
        sample = problems_by_hop[hops][:max_per_hop]

        tasks = [
            ask_multihop_question_with_thinking(p, semaphore)
            for p in sample
        ]

        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]

        correct = sum(1 for r in results if r["is_correct"])
        total = len(results)
        accuracy = correct / total * 100 if total > 0 else 0

        print(f"  {correct}/{total} ({accuracy:.1f}%)")

        results_by_hop[hops] = {
            "results": results,
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
        }

    return results_by_hop


def print_results(results_by_hop):
    """Print detailed results."""
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)

    for hops, data in sorted(results_by_hop.items()):
        accuracy = data["accuracy"]
        correct = data["correct"]
        total = data["total"]

        print(f"\n{hops}-HOP: {correct}/{total} ({accuracy:.1f}%)")

        # Show examples of failures
        failures = [r for r in data["results"] if not r["is_correct"]]
        if failures:
            print(f"  Failures ({len(failures)}):")
            for f in failures[:5]:
                print(f"    Q: {f['question']}")
                print(f"       Expected: {f['correct_answer']}")
                print(f"       Got:      {f['predicted']}")
                print(f"       Type:     {f['type']}")
                print()
        else:
            print("  ✓ All correct!")

    # Overall statistics
    total_correct = sum(data["correct"] for data in results_by_hop.values())
    total_questions = sum(data["total"] for data in results_by_hop.values())
    overall_accuracy = total_correct / total_questions * 100 if total_questions > 0 else 0

    print("\n" + "="*80)
    print(f"OVERALL: {total_correct}/{total_questions} ({overall_accuracy:.1f}%)")
    print("="*80)


async def main():
    # Load all problems
    print("Loading problems...")
    all_problems = load_problems("data/problems_all.jsonl")
    print(f"Loaded {len(all_problems)} total problems")
    print()

    # Evaluate with thinking enabled
    results = await evaluate_multihop(all_problems, max_per_hop=1000)

    # Print results
    print_results(results)

    # Count cached vs fresh requests
    total_cached = sum(
        sum(1 for r in data["results"] if r.get("cached", False))
        for data in results.values()
    )
    total_requests = sum(data["total"] for data in results.values())
    print(f"\nCache statistics: {total_cached}/{total_requests} responses from cache ({total_cached/total_requests*100:.1f}%)")

    # Save cache
    await cache.save_cache(force=True)
    print(f"Cache saved to caches/multihop_thinking_cache.json")

    # Save results
    output_file = "eval_results/multihop_thinking_verification.json"
    Path("eval_results").mkdir(exist_ok=True)
    with open(output_file, "w") as f:
        json.dump({
            "model": MODEL,
            "thinking_enabled": True,
            "thinking_budget_tokens": 10000,
            "results_by_hop": {
                str(hops): {
                    "correct": data["correct"],
                    "total": data["total"],
                    "accuracy": data["accuracy"],
                    "results": data["results"],
                }
                for hops, data in results.items()
            },
        }, f, indent=2)

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())

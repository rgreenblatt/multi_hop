#!/usr/bin/env python3
"""
Verify that Opus 4.5 can correctly answer single-hop fact questions.

This validates that the model knows the individual facts before we test multi-hop reasoning.
"""

import json
import asyncio
import sys
from pathlib import Path
from collections import defaultdict
from anthropic import AsyncAnthropic
import os
from eval_multi_hop import check_answer
from response_cache import ResponseCache

# Add parent directory to path to import generate_dataset
sys.path.insert(0, str(Path(__file__).parent))
from generate_dataset_constants import generate_single_hop_questions
from generate_dataset import generate_single_hop_questions_auto


# Get API key
api_key_file = Path.home() / ".anthropic_api_key_rr"
if api_key_file.exists():
    ANTHROPIC_API_KEY = api_key_file.read_text().strip()
else:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-opus-4-5-20251101"

# Initialize cache
cache = ResponseCache("caches/single_hop_cache.json", save_every=50)


async def ask_single_hop_question(question, correct_answer, semaphore):
    """Ask Opus 4.5 a single-hop question."""
    # Create cache key
    cache_key = {
        "model": MODEL,
        "question": question,
        "max_tokens": 50,
        "temperature": 0.0,
    }

    # Check cache first
    cached = await cache.get(cache_key)
    if cached is not None:
        predicted = cached["response"]
        is_correct = check_answer(predicted, correct_answer)
        return {
            "question": question,
            "correct_answer": correct_answer,
            "predicted": predicted,
            "is_correct": is_correct,
            "cached": True,
        }

    async with semaphore:
        prompt = f"""You will be given a question. Answer immediately using the format 'Answer: [ANSWER]' where [ANSWER] is just the answer, nothing else. No explanation, no words, no reasoning, just the answer.

Question: {question}"""

        messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": "Answer:"}]

        max_retries = 8
        for retry in range(max_retries):
            try:
                response = await anthropic_client.messages.create(
                    model=MODEL, max_tokens=50, temperature=0.0, messages=messages
                )

                predicted = response.content[0].text.strip()

                # Cache the response
                await cache.set(cache_key, {"response": predicted})

                is_correct = check_answer(predicted, correct_answer)

                return {
                    "question": question,
                    "correct_answer": correct_answer,
                    "predicted": predicted,
                    "is_correct": is_correct,
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


async def evaluate_single_hops(single_hops, max_per_type=200):
    """Evaluate Opus 4.5 on single-hop questions."""
    print("=" * 80)
    print("SINGLE-HOP FACT VERIFICATION")
    print("=" * 80)
    print(f"Model: {MODEL}")
    print()

    # Summary of what we're testing
    for fact_type, questions in single_hops.items():
        print(f"{fact_type}: {len(questions)} unique questions")
    print()

    # Run evaluations
    semaphore = asyncio.Semaphore(80)  # Limit concurrency

    results_by_type = {}

    for fact_type, questions in single_hops.items():
        print(f"\nTesting {fact_type}...")

        # Sample up to max_per_type questions
        sample = questions[:max_per_type] if len(questions) > max_per_type else questions

        tasks = [ask_single_hop_question(q, a, semaphore) for q, a in sample]

        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]

        correct = sum(1 for r in results if r["is_correct"])
        total = len(results)
        accuracy = correct / total * 100 if total > 0 else 0

        print(f"  {correct}/{total} ({accuracy:.1f}%)")

        results_by_type[fact_type] = {
            "results": results,
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
        }

    return results_by_type


def print_results(results_by_type):
    """Print detailed results."""
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    for fact_type, data in results_by_type.items():
        accuracy = data["accuracy"]
        correct = data["correct"]
        total = data["total"]

        print(f"\n{fact_type.upper()}: {correct}/{total} ({accuracy:.1f}%)")

        # Show examples of failures
        failures = [r for r in data["results"] if not r["is_correct"]]
        if failures:
            print(f"  Failures ({len(failures)}):")
            for f in failures[:5]:
                print(f"    Q: {f['question']}")
                print(f"       Expected: {f['correct_answer']}")
                print(f"       Got:      {f['predicted']}")
                print()
        else:
            print("  ✓ All correct!")

    # Overall statistics
    total_correct = sum(data["correct"] for data in results_by_type.values())
    total_questions = sum(data["total"] for data in results_by_type.values())
    overall_accuracy = total_correct / total_questions * 100 if total_questions > 0 else 0

    print("\n" + "=" * 80)
    print(f"OVERALL: {total_correct}/{total_questions} ({overall_accuracy:.1f}%)")
    print("=" * 80)

    # Flag any fact types with low accuracy
    low_accuracy_types = [
        (fact_type, data["accuracy"]) for fact_type, data in results_by_type.items() if data["accuracy"] < 95
    ]

    if low_accuracy_types:
        print("\n⚠️  WARNING: Some fact types have low accuracy:")
        for fact_type, accuracy in low_accuracy_types:
            print(f"  - {fact_type}: {accuracy:.1f}%")
        print("\nThese facts may not be reliable for multi-hop reasoning!")
    else:
        print("\n✓ All fact types have high accuracy (>95%)!")


async def main():
    # Generate single-hop questions from dataset
    print("Generating single-hop questions...")
    single_hops = {**generate_single_hop_questions(), **generate_single_hop_questions_auto()}

    # Evaluate on each type
    results = await evaluate_single_hops(single_hops, max_per_type=200)

    # Print results
    print_results(results)

    # Count cached vs fresh requests
    total_cached = sum(sum(1 for r in data["results"] if r.get("cached", False)) for data in results.values())
    total_requests = sum(data["total"] for data in results.values())
    print(
        f"\nCache statistics: {total_cached}/{total_requests} responses from cache ({total_cached/total_requests*100:.1f}%)"
    )

    # Save cache
    await cache.save_cache(force=True)
    print(f"Cache saved to caches/single_hop_cache.json")

    # Save results
    output_file = "eval_results/single_hop_verification.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "model": MODEL,
                "results_by_type": {
                    fact_type: {
                        "correct": data["correct"],
                        "total": data["total"],
                        "accuracy": data["accuracy"],
                        "results": data["results"],
                    }
                    for fact_type, data in results.items()
                },
            },
            f,
            indent=2,
        )

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())

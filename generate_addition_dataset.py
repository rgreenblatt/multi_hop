#!/usr/bin/env python3
"""
Generate addition dataset where questions add n numbers from 1-hop fact generators.

Instead of multi-hop reasoning chains, this creates questions like:
"What is (atomic number of Gold) + (atomic number of Lead)?"
"""

import json
import random
import argparse
from typing import List, Dict, Any, Tuple
from pathlib import Path

from generate_dataset_constants import (
    AGE_FACTS,
    ELEMENTS_FILTERED,
    STATIC_FACTS,
    US_HOUSE_SEATS_FACTS,
    STATE_LEGISLATURE_HOUSE_SEATS_FACTS,
)


def get_one_hop_generators() -> List[Dict[str, Any]]:
    """
    Get all 1-hop number generators (excluding fixed_num).
    Each generator produces (value, expression, fact_description) tuples.
    Filter to values >= 0 and < 100.
    """
    generators = []

    # Elements - atomic numbers
    element_items = [
        (num, f"(atomic number of {name})", f"Atomic number of {name}")
        for name, num in ELEMENTS_FILTERED.items()
        if 0 <= num < 100
    ]
    generators.append({
        "id": "element",
        "items": element_items,
    })

    # Age facts
    age_items = [
        (fact["answer"], f"({fact['question'].replace('?', '')})", fact["question"])
        for fact in AGE_FACTS
        if isinstance(fact["answer"], int) and 0 <= fact["answer"] < 100
    ]
    generators.append({
        "id": "agefact",
        "items": age_items,
    })

    # Static facts
    static_items = [
        (fact["answer"], f"({fact['question'].replace('?', '')})", fact["question"])
        for fact in STATIC_FACTS
        if isinstance(fact["answer"], int) and 0 <= fact["answer"] < 100
    ]
    generators.append({
        "id": "staticfact",
        "items": static_items,
    })

    # US House seats
    house_items = [
        (fact["answer"], f"({fact['question'].replace('?', '')})", fact["question"])
        for fact in US_HOUSE_SEATS_FACTS
        if isinstance(fact["answer"], int) and 0 <= fact["answer"] < 100
    ]
    generators.append({
        "id": "us_house_seats",
        "items": house_items,
    })

    # State legislature house seats
    state_leg_items = [
        (fact["answer"], f"({fact['question'].replace('?', '')})", fact["question"])
        for fact in STATE_LEGISLATURE_HOUSE_SEATS_FACTS
        if isinstance(fact["answer"], int) and 0 <= fact["answer"] < 100
    ]
    generators.append({
        "id": "state_leg_house_seats",
        "items": state_leg_items,
    })

    return generators


def get_all_one_hop_facts() -> List[Tuple[int, str, str]]:
    """
    Get all 1-hop facts from all generators combined.
    Returns list of (value, expression, description) tuples.
    """
    generators = get_one_hop_generators()
    all_facts = []
    for gen in generators:
        all_facts.extend(gen["items"])
    return all_facts


def generate_addition_problems(
    num_addends: int,
    num_problems: int,
    seed: int,
) -> List[Dict[str, Any]]:
    """
    Generate addition problems with num_addends numbers being added.

    Args:
        num_addends: How many numbers to add (e.g., 2 means A + B)
        num_problems: How many problems to generate
        seed: Random seed for reproducibility

    Returns:
        List of problem dicts with question, answer, chain info
    """
    random.seed(seed)

    all_facts = get_all_one_hop_facts()

    if len(all_facts) < num_addends:
        raise ValueError(f"Not enough unique facts ({len(all_facts)}) for {num_addends} addends")

    problems = []
    attempts = 0
    max_attempts = num_problems * 100  # Prevent infinite loops

    seen_questions = set()

    while len(problems) < num_problems and attempts < max_attempts:
        attempts += 1

        # Sample num_addends facts without replacement
        selected_facts = random.sample(all_facts, num_addends)

        # Build the question
        expressions = [fact[1] for fact in selected_facts]
        question = "What is " + " + ".join(expressions) + "?"

        # Skip if we've seen this exact question before
        if question in seen_questions:
            continue
        seen_questions.add(question)

        # Calculate the answer
        answer = sum(fact[0] for fact in selected_facts)

        # Build the chain (list of facts used)
        chain = [
            {"fact": fact[2], "value": fact[0]}
            for fact in selected_facts
        ]

        problems.append({
            "type": f"addition_{num_addends}",
            "question": question,
            "answer": answer,
            "num_addends": num_addends,
            "chain": chain,
        })

    if len(problems) < num_problems:
        print(f"Warning: Could only generate {len(problems)} unique problems for {num_addends} addends (requested {num_problems})")

    return problems


def save_dataset(problems: List[Dict], filepath: str):
    """Save problems to JSONL file."""
    import os
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for problem in problems:
            f.write(json.dumps(problem, ensure_ascii=False) + "\n")
    print(f"Saved {len(problems)} problems to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Generate addition dataset")
    parser.add_argument(
        "--min-addends",
        type=int,
        default=2,
        help="Minimum number of addends (default: 2)",
    )
    parser.add_argument(
        "--max-addends",
        type=int,
        default=10,
        help="Maximum number of addends (default: 10)",
    )
    parser.add_argument(
        "--num-per-count",
        type=int,
        default=100,
        help="Number of problems per addend count (default: 100)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/addition_problems.jsonl",
        help="Output file path (default: data/addition_problems.jsonl)",
    )
    args = parser.parse_args()

    # Print info about available facts
    all_facts = get_all_one_hop_facts()
    print(f"Total 1-hop facts available: {len(all_facts)}")

    generators = get_one_hop_generators()
    for gen in generators:
        print(f"  {gen['id']}: {len(gen['items'])} facts")

    # Generate problems for each addend count
    all_problems = []
    for num_addends in range(args.min_addends, args.max_addends + 1):
        seed = args.seed + num_addends  # Different seed per addend count
        problems = generate_addition_problems(
            num_addends=num_addends,
            num_problems=args.num_per_count,
            seed=seed,
        )
        all_problems.extend(problems)
        print(f"Generated {len(problems)} problems with {num_addends} addends")

    # Shuffle all problems together
    random.seed(args.seed)
    random.shuffle(all_problems)

    # Save dataset
    save_dataset(all_problems, args.output)

    # Print examples
    print("\n=== EXAMPLE PROBLEMS ===")
    for num_addends in range(args.min_addends, min(args.min_addends + 3, args.max_addends + 1)):
        examples = [p for p in all_problems if p["num_addends"] == num_addends][:2]
        print(f"\n{num_addends}-addend examples:")
        for p in examples:
            print(f"  Q: {p['question']}")
            print(f"  A: {p['answer']}")
            print(f"  Values: {[c['value'] for c in p['chain']]}")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total problems: {len(all_problems)}")
    for num_addends in range(args.min_addends, args.max_addends + 1):
        count = sum(1 for p in all_problems if p["num_addends"] == num_addends)
        print(f"  {num_addends}-addend: {count} problems")


if __name__ == "__main__":
    main()

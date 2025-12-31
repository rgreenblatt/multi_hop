#!/usr/bin/env python3
"""
Show randomly selected examples that a model got correct.
"""

import json
import argparse
import random
from collections import defaultdict
from pathlib import Path


def load_results(model_shorthand, repeat=None, filler=None):
    """Load individual problem results from eval file."""
    repeat_suffix = f"_r{repeat}" if repeat else ""
    filler_suffix = f"_f{filler}" if filler else ""
    filepath = f"eval_results/eval_{model_shorthand}_all{repeat_suffix}{filler_suffix}.json"

    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        return None

    with open(filepath) as f:
        data = json.load(f)

    return data.get("results", [])


def filter_results(results, hop_filter=None, category_filter=None, correct_only=True):
    """Filter results by hop count, category, and correctness."""
    filtered = results

    if correct_only:
        filtered = [r for r in filtered if r["is_correct"]]

    if hop_filter is not None:
        filtered = [r for r in filtered if r["hops"] == hop_filter]

    if category_filter:
        filtered = [r for r in filtered if r["type"] == category_filter]

    return filtered


def group_by_category(results):
    """Group results by problem type/category."""
    by_category = defaultdict(list)
    for r in results:
        by_category[r["type"]].append(r)
    return dict(by_category)


def show_examples(results, show_correctness=False, print_category=True, group_by_cat=True, show_hops=False):
    """Show randomly selected examples."""
    if not results:
        print("No results to show.")
        return

    if group_by_cat:
        # Group by category and show organized by category
        by_category = group_by_category(results)
        print(f"Found {len(results)} matching examples across {len(by_category)} categories\n")

        # Sort categories alphabetically
        for category in sorted(by_category.keys()):
            if print_category:
                print(f"{category}")
            for example in by_category[category]:
                is_correct = example["is_correct"]
                status = "✓ CORRECT" if is_correct else "✗ INCORRECT"
                hop_label = f"({example['hops']}-hop) " if show_hops else ""
                prefix = "  " if print_category else ""
                print(f"{prefix}{hop_label}{example['question']}" + (f" {status}" if show_correctness else ""))

            if print_category:
                print()
    else:
        # Show flat list without grouping
        print(f"\nFound {len(results)} matching examples\n")
        for example in results:
            is_correct = example["is_correct"]
            status = "✓ CORRECT" if is_correct else "✗ INCORRECT"
            category_prefix = f"[{example['type']}] " if print_category else ""
            hop_label = f"({example['hops']}-hop) " if show_hops else ""
            print(f"  {category_prefix}{hop_label}{example['question']}" + (f" {status}" if show_correctness else ""))


def list_categories(results):
    """List all available categories with counts."""
    by_category = group_by_category(results)

    print("\nAvailable categories:")
    print("-" * 60)
    print(f"{'Category':<50} {'Count':>8}")
    print("-" * 60)

    for category in sorted(by_category.keys()):
        count = len(by_category[category])
        print(f"{category:<50} {count:>8}")

    print("-" * 60)
    print(f"{'Total':<50} {len(results):>8}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Show random examples that a model got correct",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show 5 examples per category for Opus 4.5 with repeat=5
  python show_examples.py -m opus-4-5 -r 5 -n 5

  # Show only 2-hop problems
  python show_examples.py -m opus-4-5 -r 5 --hop 2

  # Show only specific category
  python show_examples.py -m opus-4-5 -r 5 -c 2hop_president_birth_year

  # List all available categories
  python show_examples.py -m opus-4-5 -r 5 --list-categories

  # Show examples with custom random seed
  python show_examples.py -m opus-4-5 -r 5 -n 10 --seed 123

  # Show examples with filler tokens
  python show_examples.py -m opus-4-5 -f 300 -n 5
        """
    )

    parser.add_argument("-m", "--model", default="opus-4",
                       help="Model shorthand (default: opus-4)")
    parser.add_argument("-r", "--repeat", type=int, default=None,
                       help="Repeat count (default: None)")
    parser.add_argument("-f", "--filler", type=int, default=None,
                       help="Filler token count (default: None)")
    parser.add_argument("-n", "--num-examples", type=int, default=20,
                       help="Number of examples to show per category (default: 10)")
    parser.add_argument("--hop", type=int, choices=[2, 3, 4],
                       help="Filter by hop count (2, 3, or 4)")
    parser.add_argument("-c", "--category", type=str,
                       help="Filter by specific category")
    parser.add_argument("--list-categories", action="store_true",
                       help="List all available categories and exit")
    parser.add_argument("--seed", type=int, default=42, nargs='?', const=None,
                       help="Random seed for reproducibility (default: 42, use --seed with no value for random)")
    parser.add_argument("--show-incorrect", action="store_true",
                       help="Show incorrect examples instead of correct ones")
    parser.add_argument("--show-all", action="store_true",
                       help="Show all examples (both correct and incorrect) with status")
    parser.add_argument("--no-category", action="store_true",
                       help="Don't print category headers/labels")
    parser.add_argument("--no-group", action="store_true",
                       help="Don't group by category, show in random order")

    args = parser.parse_args()

    # Load results
    print(f"Loading results for {args.model} (repeat={args.repeat}, filler={args.filler})...")
    results = load_results(args.model, args.repeat, args.filler)

    if results is None:
        return 1

    print(f"Loaded {len(results)} total results")

    # Determine filtering mode
    if args.show_all:
        correct_only = None  # Don't filter by correctness
    elif args.show_incorrect:
        correct_only = False  # Show only incorrect
    else:
        correct_only = True  # Show only correct (default)

    # Filter results
    if correct_only is None:
        # Don't filter by correctness
        filtered = results
        if args.hop:
            filtered = [r for r in filtered if r["hops"] == args.hop]
        if args.category:
            filtered = [r for r in filtered if r["type"] == args.category]
    else:
        filtered = filter_results(
            results,
            hop_filter=args.hop,
            category_filter=args.category,
            correct_only=correct_only
        )

    if not filtered:
        print("No results match the specified filters.")
        return 1

    # List categories or show examples
    if args.list_categories:
        list_categories(filtered)
    else:
        if args.show_all:
            status_desc = "all examples (correct and incorrect)"
        elif args.show_incorrect:
            status_desc = "incorrect examples"
        else:
            status_desc = "correct examples"

        print(f"\nShowing {status_desc}:")
        if args.hop:
            print(f"Filtered by: {args.hop}-hop problems")
        if args.category:
            print(f"Filtered by: category '{args.category}'")

        # Set random seed for reproducibility (if provided)
        if args.seed is not None:
            random.seed(args.seed)

        # If not grouping, shuffle and limit before showing
        random.shuffle(filtered)
        filtered = filtered[:args.num_examples]

        show_examples(
            filtered,
            show_correctness=args.show_all,
            print_category=not args.no_category,
            group_by_cat=not args.no_group,
            show_hops=args.hop is None
        )

    return 0


if __name__ == "__main__":
    exit(main())

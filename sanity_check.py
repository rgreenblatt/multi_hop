#!/usr/bin/env python3
import json
import sys
from collections import Counter


def check_question_format(questions_file="data/problems_all.jsonl"):
    """Check that questions don't leak intermediate values."""
    print("="*80)
    print("CHECKING QUESTION FORMAT")
    print("="*80)

    with open(questions_file) as f:
        problems = [json.loads(l) for l in f]

    issues = []
    for p in problems:
        q = p["question"]
        chain = p["chain"]

        # Check if any intermediate value appears in the question text
        for hop in chain[:-1]:  # All hops except the final answer
            value = str(hop["value"])
            # Check for numeric values that shouldn't appear
            if value.isdigit() and len(value) >= 2:  # Skip single digits as they could be part of words
                # Allow values that are part of "1900 +" formula
                if value in q and f"1900 + " not in q:
                    issues.append({
                        "question": q,
                        "leaked_value": value,
                        "hop": hop["fact"],
                    })

    print(f"Total questions: {len(problems)}")
    print(f"Questions with leaked values: {len(issues)}")

    if issues:
        print("\nExamples of leaked values:")
        for issue in issues[:5]:
            print(f"  Q: {issue['question'][:80]}...")
            print(f"     Leaked: {issue['leaked_value']} from {issue['hop']}")
            print()

    return len(issues) == 0




def main():
    # Check question format
    check_question_format()

if __name__ == "__main__":
    main()

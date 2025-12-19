#!/usr/bin/env python3
"""
Script to demonstrate what the evaluation prompts look like.
Shows the full prompt for randomly selected problems with configurable options.
"""

import argparse
import json
import random
from eval_multi_hop import (
    build_user_message,
    build_few_shot_messages,
    load_problems,
    select_few_shot_problems,
)

# Try to import anthropic for token counting
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def count_tokens_anthropic(messages: list[dict], model: str = "claude-sonnet-4-20250514") -> int | None:
    """
    Count tokens using Anthropic's official token counting API.
    Returns None if counting fails.
    """
    if not ANTHROPIC_AVAILABLE:
        return None

    try:
        client = anthropic.Anthropic()
        # Convert our message format to Anthropic's expected format
        formatted_messages = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                content = "\n".join(text_parts)
            formatted_messages.append({"role": msg["role"], "content": content})

        response = client.beta.messages.count_tokens(
            model=model,
            messages=formatted_messages,
        )
        return response.input_tokens
    except Exception as e:
        print(f"Warning: Token counting failed: {e}")
        return None


def estimate_tokens_simple(text: str) -> int:
    """
    Simple token estimation based on character count.
    Roughly 4 characters per token for English text.
    This is a fallback when API counting is not available.
    """
    return len(text) // 4


def count_message_tokens(messages: list[dict], use_api: bool = True) -> tuple[int, str]:
    """
    Count tokens for a list of messages.
    Returns (token_count, method_used).
    """
    if use_api and ANTHROPIC_AVAILABLE:
        token_count = count_tokens_anthropic(messages)
        if token_count is not None:
            return token_count, "anthropic-api"

    # Fallback to simple estimation
    total_text = ""
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    total_text += block.get("text", "") + "\n"
        else:
            total_text += content + "\n"

    return estimate_tokens_simple(total_text), "estimate (~4 chars/token)"


def show_prompts(
    input_file: str,
    num_examples: int = 1,
    k_shot: int = 10,
    repeat_problem: int | None = None,
    include_mappings: bool = False,
    mapping_position: str = "before",
    seed: int | None = None,
    show_few_shot: bool = True,
    count_tokens: bool = False,
):
    """Show example prompts for randomly selected problems."""
    problems = load_problems(input_file)

    if len(problems) <= k_shot:
        print(f"Warning: Only {len(problems)} problems, reducing k_shot to {len(problems) - 1}")
        k_shot = max(1, len(problems) - 1)

    # Select few-shot examples
    few_shot_problems, few_shot_indices = select_few_shot_problems(problems, k_shot=k_shot)

    # Select random problems to show (excluding few-shot examples)
    available_indices = [i for i in range(len(problems)) if i not in few_shot_indices]

    if seed is not None:
        random.seed(seed)

    num_to_show = min(num_examples, len(available_indices))
    selected_indices = random.sample(available_indices, num_to_show)

    # Build few-shot messages once
    few_shot_messages = build_few_shot_messages(
        few_shot_problems,
        repeat_problem=repeat_problem,
        cache=False,
        include_mappings=include_mappings,
        mapping_position=mapping_position,
    )

    for example_num, problem_idx in enumerate(selected_indices, 1):
        problem = problems[problem_idx]

        print("=" * 80)
        print(f"EXAMPLE {example_num} OF {num_to_show} (Problem index: {problem_idx})")
        print("=" * 80)

        # Show problem metadata
        print(f"\n--- Problem Metadata ---")
        print(f"Type: {problem.get('type', 'unknown')}")
        print(f"Hops: {problem.get('hops', 'unknown')}")
        print(f"Question: {problem.get('question', problem.get('problem', ''))}")
        print(f"Answer: {problem.get('answer', 'unknown')}")
        print(f"Chain: {' -> '.join(str(step.get('value', '?')) for step in problem.get('chain', []))}")

        if include_mappings:
            print(f"\nMapping IDs in chain:")
            for i, step in enumerate(problem.get("chain", []), 1):
                mapping_id = step.get("mapping_id", "none")
                print(f"  Step {i}: {mapping_id}")

        # Show few-shot section if enabled
        if show_few_shot:
            print(f"\n--- Few-Shot Examples ({k_shot} examples) ---")
            for i, msg in enumerate(few_shot_messages):
                role = msg["role"]
                if role == "user":
                    content = msg["content"]
                    if isinstance(content, list):
                        text = content[0].get("text", "")
                    else:
                        text = content
                    # Truncate for display
                    if len(text) > 500:
                        text = text[:500] + f"\n... [truncated, {len(text)} chars total]"
                    print(f"\n[USER {i//2 + 1}]:")
                    print(text)
                else:
                    print(f"\n[ASSISTANT {i//2 + 1}]:")
                    print(msg["content"])

        # Show the actual problem prompt
        print(f"\n--- Problem Prompt ---")
        user_message = build_user_message(
            problem,
            repeat_problem=repeat_problem,
            include_mappings=include_mappings,
            mapping_position=mapping_position,
        )
        print(f"\n[USER (problem)]:")
        print(user_message)

        print(f"\n[ASSISTANT (prefill)]:")
        print("Answer:")

        # Show expected answer
        print(f"\n--- Expected Answer ---")
        print(f"Answer: {problem.get('answer', 'unknown')}")

        # Show token count if requested
        if count_tokens:
            print(f"\n--- Token Count ---")
            # Build the full message list as it would be sent to the API
            full_messages = few_shot_messages + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "Answer:"},
            ]

            # Count tokens for different parts
            few_shot_tokens, fs_method = count_message_tokens(few_shot_messages, use_api=True)
            problem_only_messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "Answer:"},
            ]
            problem_tokens, prob_method = count_message_tokens(problem_only_messages, use_api=True)
            total_tokens, total_method = count_message_tokens(full_messages, use_api=True)

            print(f"Few-shot examples: ~{few_shot_tokens:,} tokens ({fs_method})")
            print(f"Problem prompt: ~{problem_tokens:,} tokens ({prob_method})")
            print(f"Total input: ~{total_tokens:,} tokens ({total_method})")

        if example_num < num_to_show:
            print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Show example evaluation prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show 1 prompt with default settings
  python show_prompt.py

  # Show 3 prompts with mappings included before the question
  python show_prompt.py -n 3 --include-mappings --mapping-position before

  # Show prompt with repeat and mappings
  python show_prompt.py --repeat-problem 2 --include-mappings

  # Use a specific input file
  python show_prompt.py -i data/problems_2hop.jsonl -n 2

  # Hide few-shot examples to focus on the problem prompt
  python show_prompt.py --no-few-shot --include-mappings

  # Show token counts (uses Anthropic API)
  python show_prompt.py --count-tokens --include-mappings
        """,
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        default="data/problems_all.jsonl",
        help="Input JSONL file with problems (default: data/problems_all.jsonl)",
    )
    parser.add_argument(
        "--num-examples", "-n",
        type=int,
        default=1,
        help="Number of example prompts to show (default: 1)",
    )
    parser.add_argument(
        "--k-shot", "-k",
        type=int,
        default=10,
        help="Number of few-shot examples (default: 10)",
    )
    parser.add_argument(
        "--repeat-problem", "-r",
        type=int,
        default=None,
        help="Number of times to repeat the problem (default: None)",
    )
    parser.add_argument(
        "--include-mappings",
        action="store_true",
        help="Include mapping tables in the prompt context",
    )
    parser.add_argument(
        "--mapping-position",
        type=str,
        default="before",
        choices=["before", "after"],
        help="Position of mapping tables relative to question (default: before)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducible selection (default: None)",
    )
    parser.add_argument(
        "--no-few-shot",
        action="store_true",
        help="Hide the few-shot examples section (only show problem prompt)",
    )
    parser.add_argument(
        "--count-tokens", "-t",
        action="store_true",
        help="Count and display approximate token counts using Anthropic API",
    )

    args = parser.parse_args()

    print(f"Configuration:")
    print(f"  Input: {args.input}")
    print(f"  Num examples: {args.num_examples}")
    print(f"  K-shot: {args.k_shot}")
    print(f"  Repeat problem: {args.repeat_problem}")
    print(f"  Include mappings: {args.include_mappings}")
    if args.include_mappings:
        print(f"  Mapping position: {args.mapping_position}")
    print(f"  Seed: {args.seed}")
    print(f"  Show few-shot: {not args.no_few_shot}")
    print(f"  Count tokens: {args.count_tokens}")
    print()

    show_prompts(
        input_file=args.input,
        num_examples=args.num_examples,
        k_shot=args.k_shot,
        repeat_problem=args.repeat_problem,
        include_mappings=args.include_mappings,
        mapping_position=args.mapping_position,
        seed=args.seed,
        show_few_shot=not args.no_few_shot,
        count_tokens=args.count_tokens,
    )


if __name__ == "__main__":
    main()

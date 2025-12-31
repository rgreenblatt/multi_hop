#!/usr/bin/env python3
"""
Run all evaluations for multi-hop reasoning experiments.
"""

import subprocess
import json
import os
from datetime import datetime

# Models to evaluate
MODELS = ["opus-4-5", "opus-4", "sonnet-4", "sonnet-4-5", "haiku-3-5", "qwen3-235b", "gpt-4.1", "gpt-5.1", "gpt-5.2", "deepseek-v3"]

# Repeat conditions
REPEATS = [None, 5]

MODELS_FOR_FILLER = ["opus-4-5", "opus-4", "gemini-2.5-pro", "gemini-3-pro"]

# Filler values to test
FILLERS = [None, 300]

# Extra repeat values for opus-4 only
OPUS4_EXTRA_REPEATS = [2, 3, 10, 20, 40]

# Extra repeat values for opus-4-5
OPUS45_EXTRA_REPEATS = [2, 3, 10, 20]


OPUS4_FILLER_SWEEP = [10, 30, 100, 300, 1000]
OPUS45_FILLER_SWEEP = [30, 100, 300, 1000]

# Input files
INPUT_FILES = {
    "all": "data/problems_all.jsonl",
    "2hop": "data/problems_2hop.jsonl",
    "3hop": "data/problems_3hop.jsonl",
    "4hop": "data/problems_4hop.jsonl",
}

# Track total costs
total_costs = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_creation_tokens": 0,
    "estimated_cost_usd": 0.0,
}


def run_eval(model, repeat, input_key="all", verbosity=2, filler=None):
    """Run a single evaluation."""
    input_file = INPUT_FILES[input_key]
    repeat_suffix = f"_r{repeat}" if repeat else ""
    filler_suffix = f"_f{filler}" if filler else ""
    output_file = f"eval_results/eval_{model}_{input_key}{repeat_suffix}{filler_suffix}.json"

    cmd = [
        "python", "eval_multi_hop.py",
        "-m", model,
        "-i", input_file,
        "-o", output_file,
        "-c", "300",
        "-v", str(verbosity),
    ]
    if "gemini" in model:
        cmd.extend(["--k-shot", "20"])
    if repeat:
        cmd.extend(["-r", str(repeat)])
    if filler:
        cmd.extend(["-f", str(filler)])

    print(f"\n{'='*60}")
    print(f"Running: {model}, repeat={repeat}, filler={filler}, input={input_key}")
    print(f"Output: {output_file}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, capture_output=False)

    # Load results and accumulate costs
    if os.path.exists(output_file):
        with open(output_file) as f:
            data = json.load(f)
        summary = data.get("summary", {})
        cost_tracker = summary.get("cost_tracker", {})

        # Only count non-cached tokens
        total_costs["input_tokens"] += cost_tracker.get("input_tokens", 0)
        total_costs["output_tokens"] += cost_tracker.get("output_tokens", 0)
        total_costs["cache_read_tokens"] += cost_tracker.get("cache_read_tokens", 0)
        total_costs["cache_creation_tokens"] += cost_tracker.get("cache_creation_tokens", 0)

        return summary
    return None


def main():
    """Run all evaluations."""
    print("="*60)
    print("MULTI-HOP REASONING EVALUATION")
    print(f"Started at: {datetime.now()}")
    print("="*60)

    results = []

    # Run evaluations on all problems for each model and repeat condition
    for model in MODELS:
        for repeat in REPEATS:
            summary = run_eval(model, repeat, "all")
            if summary:
                results.append({
                    "model": model,
                    "repeat": repeat,
                    "input": "all",
                    **summary,
                })

    for model in MODELS_FOR_FILLER:
        for filler in FILLERS:
            summary = run_eval(model, repeat=None, input_key="all", filler=filler)
            if summary:
                results.append({
                    "model": model,
                    "filler": filler,
                    "input": "all",
                    **summary,
                })

    # Run extra repeat values for opus-4 only
    for repeat in OPUS4_EXTRA_REPEATS:
        summary = run_eval("opus-4", repeat, "all")
        if summary:
            results.append({
                "model": "opus-4",
                "repeat": repeat,
                "input": "all",
                **summary,
            })

    # Run extra repeat values for opus-4-5
    for repeat in OPUS45_EXTRA_REPEATS:
        summary = run_eval("opus-4-5", repeat, "all")
        if summary:
            results.append({
                "model": "opus-4-5",
                "repeat": repeat,
                "input": "all",
                **summary,
            })

    # Run filler sweep for opus-4
    for filler in OPUS4_FILLER_SWEEP:
        summary = run_eval("opus-4", None, "all", filler=filler)
        if summary:
            results.append({
                "model": "opus-4",
                "repeat": None,
                "filler": filler,
                "input": "all",
                **summary,
            })

    # Run filler sweep for opus-4-5
    for filler in OPUS45_FILLER_SWEEP:
        summary = run_eval("opus-4-5", None, "all", filler=filler)
        if summary:
            results.append({
                "model": "opus-4-5",
                "repeat": None,
                "filler": filler,
                "input": "all",
                **summary,
            })

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY OF ALL RUNS")
    print("="*60)

    # Calculate column widths dynamically
    def get_val(r, key, default="-"):
        v = r.get(key)
        return str(v) if v is not None else default

    col_model = max(len("Model"), max((len(get_val(r, "model", "unknown")) for r in results), default=5))
    col_repeat = max(len("Repeat"), 6)
    col_filler = max(len("Filler"), 6)
    col_total = max(len("Total"), 6)
    col_correct = max(len("Correct"), 7)
    col_accuracy = max(len("Accuracy"), 8)

    header = f"{'Model':<{col_model}}  {'Repeat':>{col_repeat}}  {'Filler':>{col_filler}}  {'Total':>{col_total}}  {'Correct':>{col_correct}}  {'Accuracy':>{col_accuracy}}"
    print(f"\n{header}")
    print("-" * len(header))
    for r in results:
        model_str = get_val(r, "model", "unknown")
        repeat_str = get_val(r, "repeat")
        filler_str = get_val(r, "filler")
        total_str = str(r.get("total", 0))
        correct_str = str(r.get("correct", 0))
        accuracy_str = f"{r.get('accuracy', 0)*100:.1f}%"
        print(f"{model_str:<{col_model}}  {repeat_str:>{col_repeat}}  {filler_str:>{col_filler}}  {total_str:>{col_total}}  {correct_str:>{col_correct}}  {accuracy_str:>{col_accuracy}}")

    # Print by hop level
    print("\n\nBY HOP LEVEL:")

    def fmt_hop(hop_stats, h):
        stats = hop_stats.get(str(h), {})
        if stats:
            return f"{stats.get('correct', 0)}/{stats.get('total', 0)} ({stats.get('correct', 0)/stats.get('total', 1)*100:.1f}%)"
        return "-"

    # Calculate hop column widths
    col_2hop = max(len("2-hop"), max((len(fmt_hop(r.get("hop_stats", {}), 2)) for r in results), default=5))
    col_3hop = max(len("3-hop"), max((len(fmt_hop(r.get("hop_stats", {}), 3)) for r in results), default=5))
    col_4hop = max(len("4-hop"), max((len(fmt_hop(r.get("hop_stats", {}), 4)) for r in results), default=5))

    header2 = f"{'Model':<{col_model}}  {'Repeat':>{col_repeat}}  {'Filler':>{col_filler}}  {'2-hop':>{col_2hop}}  {'3-hop':>{col_3hop}}  {'4-hop':>{col_4hop}}"
    print("-" * len(header2))
    print(header2)
    print("-" * len(header2))
    for r in results:
        model_str = get_val(r, "model", "unknown")
        repeat_str = get_val(r, "repeat")
        filler_str = get_val(r, "filler")
        hop_stats = r.get("hop_stats", {})
        print(f"{model_str:<{col_model}}  {repeat_str:>{col_repeat}}  {filler_str:>{col_filler}}  {fmt_hop(hop_stats, 2):>{col_2hop}}  {fmt_hop(hop_stats, 3):>{col_3hop}}  {fmt_hop(hop_stats, 4):>{col_4hop}}")

    # Print cost summary
    print("\n" + "="*60)
    print("COST SUMMARY (non-cached calls only)")
    print("="*60)
    print(f"Input tokens:          {total_costs['input_tokens']:,}")
    print(f"Output tokens:         {total_costs['output_tokens']:,}")
    print(f"Cache read tokens:     {total_costs['cache_read_tokens']:,}")
    print(f"Cache creation tokens: {total_costs['cache_creation_tokens']:,}")

    # Estimate total cost (using average pricing)
    # This is approximate since we're mixing models
    avg_input_price = 9.0  # Average of opus and sonnet
    avg_output_price = 45.0
    estimated_cost = (
        total_costs["input_tokens"] * avg_input_price / 1_000_000
        + total_costs["output_tokens"] * avg_output_price / 1_000_000
    )
    print(f"\nEstimated total cost: ${estimated_cost:.2f}")

    # Save summary
    summary_file = "eval_results/all_runs_summary.json"
    with open(summary_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "total_costs": total_costs,
        }, f, indent=2)
    print(f"\nSummary saved to: {summary_file}")


if __name__ == "__main__":
    main()

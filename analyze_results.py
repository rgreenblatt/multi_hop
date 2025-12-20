#!/usr/bin/env python3
"""
Analyze and visualize multi-hop reasoning results.
"""

import random
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns
import os
import glob
from eval_multi_hop import normalize_answer
from collections import Counter

# Load results
with open("eval_results/all_runs_summary.json") as f:
    data = json.load(f)

results = data["results"]


def wilson_score_interval(successes, n, confidence=0.95):
    """
    Calculate Wilson score confidence interval for a proportion.
    More accurate than normal approximation, especially for extreme proportions.
    """
    if n == 0:
        return 0, 0

    p = successes / n
    z = stats.norm.ppf((1 + confidence) / 2)

    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

    return max(0, center - margin), min(1, center + margin)


def load_individual_results(model_shorthand, repeat=None):
    """Load individual problem results from eval file."""
    repeat_suffix = f"_r{repeat}" if repeat else ""
    filepath = f"eval_results/eval_{model_shorthand}_all{repeat_suffix}.json"

    if not os.path.exists(filepath):
        return None

    with open(filepath) as f:
        data = json.load(f)

    return data.get("results", [])


def paired_t_test(results_baseline, results_repeat):
    """
    Perform paired t-test comparing baseline vs repeat.
    Returns (t_statistic, p_value).
    """
    # Match problems by index
    baseline_dict = {r["problem_index"]: r["is_correct"] for r in results_baseline}
    repeat_dict = {r["problem_index"]: r["is_correct"] for r in results_repeat}

    # Get matched pairs
    indices = sorted(set(baseline_dict.keys()) & set(repeat_dict.keys()))

    baseline_scores = [int(baseline_dict[i]) for i in indices]
    repeat_scores = [int(repeat_dict[i]) for i in indices]

    if len(baseline_scores) < 2:
        return None, None

    # Paired t-test
    t_stat, p_value = stats.ttest_rel(repeat_scores, baseline_scores)

    return t_stat, p_value


# Model display names and colors
MODEL_NAMES = {
    "claude-opus-4-5-20251101": "Opus 4.5",
    "claude-opus-4-20250514": "Opus 4",
    "claude-sonnet-4-20250514": "Sonnet 4",
    "claude-sonnet-4-5-20250929": "Sonnet 4.5",
    "claude-3-5-haiku-20241022": "Haiku 3.5",
}

# Reverse mapping for loading individual results
MODEL_SHORTHAND = {
    "Opus 4.5": "opus-4-5",
    "Opus 4": "opus-4",
    "Sonnet 4": "sonnet-4",
    "Sonnet 4.5": "sonnet-4-5",
    "Haiku 3.5": "haiku-3-5",
}

MODEL_COLORS = {
    "Opus 4.5": "#E74C3C",
    "Opus 4": "#3498DB",
    "Sonnet 4": "#2ECC71",
    "Sonnet 4.5": "#9B59B6",
    "Haiku 3.5": "#F39C12",
}

# Model release dates (approximate)
MODEL_DATES = {
    "Haiku 3.5": "2024-10",
    "Opus 4": "2025-05",
    "Sonnet 4": "2025-05",
    "Sonnet 4.5": "2025-09",
    "Opus 4.5": "2025-11",
}


def extract_data():
    """Extract data into a more usable format."""
    data_by_model = {}

    for r in results:
        model = MODEL_NAMES.get(r.get("model"), r.get("model"))
        repeat = r.get("repeat")
        if r.get("filler") is not None:
            continue

        if model not in data_by_model:
            data_by_model[model] = {}

        key = f"r{repeat}" if repeat else "baseline"
        data_by_model[model][key] = {
            "accuracy": r.get("accuracy", 0),
            "hop_stats": r.get("hop_stats", {}),
        }

    return data_by_model


def plot_accuracy_by_hops():
    """Plot accuracy by number of hops for each model."""
    data_by_model = extract_data()

    fig = plt.figure(figsize=(14, 10))
    # 2 top, 1 bottom centered layout using GridSpec
    gs = fig.add_gridspec(2, 4, hspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0:2])
    ax2 = fig.add_subplot(gs[0, 2:4])
    ax3 = fig.add_subplot(gs[1, 1:3])  # Centered in bottom row

    hops = [2, 3, 4]
    x = np.arange(len(hops)) * 1.3  # Spacing between hop groups
    width = 0.2

    # Baseline (no repeat)
    ax = ax1
    ax.set_title("Accuracy by Hop Level (Baseline, r=1)", fontsize=14)

    for i, (model, model_data) in enumerate(data_by_model.items()):
        baseline = model_data.get("baseline", {})
        hop_stats = baseline.get("hop_stats", {})

        accuracies = []
        for h in hops:
            stats_h = hop_stats.get(str(h), {})
            if stats_h:
                acc = stats_h.get("correct", 0) / stats_h.get("total", 1)
            else:
                acc = 0
            accuracies.append(acc * 100)

        bars = ax.bar(x + i * width, accuracies, width, label=model, color=MODEL_COLORS.get(model, "gray"))

        # Add value labels
        for bar, acc in zip(bars, accuracies):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{acc:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xlabel("Number of Hops")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(hops)
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)

    # With repeat (r=5)
    ax = ax2
    ax.set_title("Accuracy by Hop Level (With Repeat, r=5)", fontsize=14)

    for i, (model, model_data) in enumerate(data_by_model.items()):
        repeat_data = model_data.get("r5", {})
        hop_stats = repeat_data.get("hop_stats", {})

        accuracies = []
        for h in hops:
            stats_h = hop_stats.get(str(h), {})
            if stats_h:
                acc = stats_h.get("correct", 0) / stats_h.get("total", 1)
            else:
                acc = 0
            accuracies.append(acc * 100)

        bars = ax.bar(x + i * width, accuracies, width, label=model, color=MODEL_COLORS.get(model, "gray"))

        for bar, acc in zip(bars, accuracies):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{acc:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xlabel("Number of Hops")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(hops)
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)

    # Bottom: Improvement from baseline to repeat
    ax = ax3
    ax.set_title("Improvement from Repeat (r=5 - r=1)", fontsize=14)

    for i, (model, model_data) in enumerate(data_by_model.items()):
        baseline_stats = model_data.get("baseline", {}).get("hop_stats", {})
        repeat_stats = model_data.get("r5", {}).get("hop_stats", {})

        improvements = []
        for h in hops:
            b_stats = baseline_stats.get(str(h), {})
            r_stats = repeat_stats.get(str(h), {})

            baseline_acc = b_stats.get("correct", 0) / b_stats.get("total", 1) * 100 if b_stats else 0
            repeat_acc = r_stats.get("correct", 0) / r_stats.get("total", 1) * 100 if r_stats else 0
            improvements.append(repeat_acc - baseline_acc)

        bars = ax.bar(x + i * width, improvements, width, label=model, color=MODEL_COLORS.get(model, "gray"))

        for bar, imp in zip(bars, improvements):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3 if imp >= 0 else bar.get_height() - 0.8,
                f"{imp:+.1f}%",
                ha="center",
                va="bottom" if imp >= 0 else "top",
                fontsize=8,
            )

    ax.set_xlabel("Number of Hops")
    ax.set_ylabel("Accuracy Improvement (%)")
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(hops)
    ax.legend()
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_ylim(-3, 12)
    ax.grid(axis="y", alpha=0.3)
    plt.savefig("eval_results/accuracy_by_hops.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: eval_results/accuracy_by_hops.png")


def plot_repeat_effect():
    """Plot the effect of repeating questions with p-values from paired t-tests."""
    data_by_model = extract_data()

    fig, ax = plt.subplots(figsize=(12, 6))

    models = list(data_by_model.keys())
    x = np.arange(len(models))
    width = 0.35

    baseline_accs = []
    repeat_accs = []
    p_values = []

    for model in models:
        baseline_accs.append(data_by_model[model].get("baseline", {}).get("accuracy", 0) * 100)
        repeat_accs.append(data_by_model[model].get("r5", {}).get("accuracy", 0) * 100)

        # Load individual results and compute p-value
        model_shorthand = MODEL_SHORTHAND.get(model)
        if model_shorthand:
            results_baseline = load_individual_results(model_shorthand, repeat=None)
            results_repeat = load_individual_results(model_shorthand, repeat=5)

            if results_baseline and results_repeat:
                t_stat, p_value = paired_t_test(results_baseline, results_repeat)
                p_values.append(p_value)
            else:
                p_values.append(None)
        else:
            p_values.append(None)

    bars1 = ax.bar(x - width / 2, baseline_accs, width, label="Baseline (r=1)", color="#3498DB")
    bars2 = ax.bar(x + width / 2, repeat_accs, width, label="Repeat (r=5)", color="#E74C3C")

    # Add value labels and p-values
    for i, (bar, acc) in enumerate(zip(bars1, baseline_accs)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{acc:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    for i, (bar, acc) in enumerate(zip(bars2, repeat_accs)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{acc:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

        # Add p-value annotation above the bar
        p_val = p_values[i]
        if p_val is not None:
            if p_val < 0.001:
                p_text = "p<0.001"
            else:
                p_text = f"p={p_val:.3f}"

            # Draw line connecting the two bars (raise it higher to avoid overlap)
            y_max = max(baseline_accs[i], repeat_accs[i]) + 4
            ax.plot([x[i] - width / 2, x[i] + width / 2], [y_max, y_max], "k-", linewidth=1)
            ax.text(x[i], y_max + 0.8, p_text, ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Overall Accuracy (%)", fontsize=12)
    ax.set_title(
        "Effect of Repeating Question 5 Times on Multi-Hop Reasoning\n(with paired t-test p-values)", fontsize=14
    )
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim(0, 90)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("eval_results/repeat_effect.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: eval_results/repeat_effect.png")


def plot_hop_decay():
    """Plot how accuracy decays with more hops."""
    data_by_model = extract_data()

    fig, ax = plt.subplots(figsize=(10, 6))

    hops = [2, 3, 4]

    for model, model_data in data_by_model.items():
        # Use r=5 data for cleaner signal
        repeat_data = model_data.get("r5", model_data.get("baseline", {}))
        hop_stats = repeat_data.get("hop_stats", {})

        accuracies = []
        for h in hops:
            stats_h = hop_stats.get(str(h), {})
            if stats_h:
                acc = stats_h.get("correct", 0) / stats_h.get("total", 1)
            else:
                acc = 0
            accuracies.append(acc * 100)

        ax.plot(hops, accuracies, "o-", label=model, color=MODEL_COLORS.get(model, "gray"), linewidth=2, markersize=10)

    ax.set_xlabel("Number of Hops", fontsize=12)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.set_title("Accuracy Decay with Increasing Hop Count (r=5)", fontsize=14)
    ax.set_xticks(hops)
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("eval_results/hop_decay.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: eval_results/hop_decay.png")


def plot_repeat_effect_by_hops():
    """Plot repeat effect broken down by hop level with p-values."""
    data_by_model = extract_data()

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    hops = [2, 3, 4]

    for idx, hop in enumerate(hops):
        ax = axes[idx]
        ax.set_title(f"{hop}-Hop Problems\n(paired t-test p-values)", fontsize=13)

        models = list(data_by_model.keys())
        x = np.arange(len(models))
        width = 0.35

        baseline_accs = []
        repeat_accs = []
        p_values = []

        for model in models:
            baseline_stats = data_by_model[model].get("baseline", {}).get("hop_stats", {}).get(str(hop), {})
            repeat_stats = data_by_model[model].get("r5", {}).get("hop_stats", {}).get(str(hop), {})

            baseline_acc = (
                baseline_stats.get("correct", 0) / baseline_stats.get("total", 1) * 100 if baseline_stats else 0
            )
            repeat_acc = repeat_stats.get("correct", 0) / repeat_stats.get("total", 1) * 100 if repeat_stats else 0

            baseline_accs.append(baseline_acc)
            repeat_accs.append(repeat_acc)

            # Load individual results and filter by hop
            model_shorthand = MODEL_SHORTHAND.get(model)
            if model_shorthand:
                results_baseline = load_individual_results(model_shorthand, repeat=None)
                results_repeat = load_individual_results(model_shorthand, repeat=5)

                if results_baseline and results_repeat:
                    # Filter by hop level
                    results_baseline_hop = [r for r in results_baseline if r.get("hops") == hop]
                    results_repeat_hop = [r for r in results_repeat if r.get("hops") == hop]

                    if results_baseline_hop and results_repeat_hop:
                        t_stat, p_value = paired_t_test(results_baseline_hop, results_repeat_hop)
                        p_values.append(p_value)
                    else:
                        p_values.append(None)
                else:
                    p_values.append(None)
            else:
                p_values.append(None)

        bars1 = ax.bar(x - width / 2, baseline_accs, width, label="r=1", color="#3498DB")
        bars2 = ax.bar(x + width / 2, repeat_accs, width, label="r=5", color="#E74C3C")

        # Add p-value annotations
        for i in range(len(models)):
            p_val = p_values[i]
            if p_val is not None:
                if p_val < 0.001:
                    p_text = "p<0.001"
                else:
                    p_text = f"p={p_val:.3f}"

                # Draw line connecting the two bars
                y_max = max(baseline_accs[i], repeat_accs[i]) + 3
                ax.plot([x[i] - width / 2, x[i] + width / 2], [y_max, y_max], "k-", linewidth=1)
                ax.text(x[i], y_max + 1, p_text, ha="center", va="bottom", fontsize=9)

        ax.set_xlabel("Model", fontsize=11)
        ax.set_ylabel("Accuracy (%)", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace(" ", "\n") for m in models], fontsize=9)
        ax.legend(fontsize=10)
        ax.set_ylim(0, 110)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("eval_results/repeat_effect_by_hops.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: eval_results/repeat_effect_by_hops.png")


def create_summary_table():
    """Create a markdown summary table."""
    data_by_model = extract_data()

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY TABLE")
    print("=" * 80)

    # Overall accuracy table
    print("\n### Overall Accuracy\n")
    print("| Model | Baseline (r=1) | Repeat (r=5) | Improvement |")
    print("|-------|----------------|--------------|-------------|")

    for model, model_data in data_by_model.items():
        baseline = model_data.get("baseline", {}).get("accuracy", 0) * 100
        repeat = model_data.get("r5", {}).get("accuracy", 0) * 100
        improvement = repeat - baseline
        print(f"| {model} | {baseline:.1f}% | {repeat:.1f}% | +{improvement:.1f}% |")

    # By hop level
    print("\n### Accuracy by Hop Level (r=5)\n")
    print("| Model | 2-hop | 3-hop | 4-hop |")
    print("|-------|-------|-------|-------|")

    for model, model_data in data_by_model.items():
        hop_stats = model_data.get("r5", {}).get("hop_stats", {})

        accs = []
        for h in [2, 3, 4]:
            stats_h = hop_stats.get(str(h), {})
            if stats_h:
                acc = stats_h.get("correct", 0) / stats_h.get("total", 1) * 100
            else:
                acc = 0
            accs.append(f"{acc:.1f}%")

        print(f"| {model} | {accs[0]} | {accs[1]} | {accs[2]} |")

    # Per-hop improvement from repeats
    print("\n### Improvement from Repeats (r=5 vs r=1) by Hop Level\n")
    print("| Model | 2-hop | 3-hop | 4-hop |")
    print("|-------|-------|-------|-------|")

    for model, model_data in data_by_model.items():
        baseline_stats = model_data.get("baseline", {}).get("hop_stats", {})
        repeat_stats = model_data.get("r5", {}).get("hop_stats", {})

        improvements = []
        for h in [2, 3, 4]:
            b_stats = baseline_stats.get(str(h), {})
            r_stats = repeat_stats.get(str(h), {})

            baseline_acc = b_stats.get("correct", 0) / b_stats.get("total", 1) * 100 if b_stats else 0
            repeat_acc = r_stats.get("correct", 0) / r_stats.get("total", 1) * 100 if r_stats else 0

            imp = repeat_acc - baseline_acc
            improvements.append(f"{imp:+.1f}%")

        print(f"| {model} | {improvements[0]} | {improvements[1]} | {improvements[2]} |")


def calculate_costs():
    """Calculate total API costs."""
    print("\n" + "=" * 80)
    print("COST SUMMARY")
    print("=" * 80)

    total_costs = data.get("total_costs", {})

    # Pricing per million tokens
    opus_input = 15.0
    opus_output = 75.0
    sonnet_input = 3.0
    sonnet_output = 15.0

    # Rough estimate (mix of opus and sonnet)
    # We ran 4 models x 2 conditions = 8 runs
    # Half were opus, half were sonnet

    input_tokens = total_costs.get("input_tokens", 0)
    output_tokens = total_costs.get("output_tokens", 0)
    cache_read = total_costs.get("cache_read_tokens", 0)
    cache_write = total_costs.get("cache_creation_tokens", 0)

    # Estimate cost (conservative - using opus pricing)
    estimated_cost = (
        input_tokens * opus_input / 1_000_000
        + output_tokens * opus_output / 1_000_000
        + cache_read * 1.5 / 1_000_000
        + cache_write * 18.75 / 1_000_000
    )

    print(f"\nTotal input tokens:  {input_tokens:,}")
    print(f"Total output tokens: {output_tokens:,}")
    print(f"Cache read tokens:   {cache_read:,}")
    print(f"Cache write tokens:  {cache_write:,}")
    print(f"\nEstimated total cost (upper bound): ${estimated_cost:.2f}")
    print(f"Budget remaining: ${10000 - estimated_cost:.2f}")


# Model configurations for r-sweep analysis
R_SWEEP_MODELS = {
    "opus-4": {
        "full_name": "claude-opus-4-20250514",
        "display_name": "Opus 4",
        "shorthand": "opus-4",
        "color": "#3498DB",
    },
    "opus-4-5": {
        "full_name": "claude-opus-4-5-20251101",
        "display_name": "Opus 4.5",
        "shorthand": "opus-4-5",
        "color": "#E74C3C",
    },
}

# Filler sweep configurations
FILLER_SWEEP_MODELS = {
    "opus-4": {
        "full_name": "claude-opus-4-20250514",
        "display_name": "Opus 4",
        "shorthand": "opus-4",
        "color": "#3498DB",
        "filler_values": [10, 30, 100, 300, 1000],
    },
    "opus-4-5": {
        "full_name": "claude-opus-4-5-20251101",
        "display_name": "Opus 4.5",
        "shorthand": "opus-4-5",
        "color": "#E74C3C",
        "filler_values": [30, 100, 300],
    },
}


def get_model_r_values(model_key):
    """Get all r values available for a model."""
    model_full_name = R_SWEEP_MODELS[model_key]["full_name"]
    r_values = []
    for r in results:
        if r.get("model") == model_full_name:
            repeat = r.get("repeat")
            if r.get("filler") is not None:
                continue
            r_val = 1 if repeat is None else repeat
            r_values.append(r_val)
    return sorted(set(r_values))


def plot_performance_vs_r():
    """Plot performance vs repeat count (r) for all models, one graph per hop level."""
    hops = [2, 3, 4]

    # Annotation positions: Opus 4 above, Opus 4.5 below
    annotation_offsets = {
        "opus-4": (0, 10),
        "opus-4-5": (0, -18),
    }

    # Collect data for all models
    model_hop_accuracies = {}
    for model_key, model_config in R_SWEEP_MODELS.items():
        model_full_name = model_config["full_name"]
        display_name = model_config["display_name"]
        color = model_config["color"]

        hop_accuracies = {2: [], 3: [], 4: []}

        # r=1 is stored as repeat=None, others as repeat=r
        for r in results:
            repeat = r.get("repeat")
            filler = r.get("filler")
            if r.get("model") == model_full_name and filler is None:
                r_val = 1 if repeat is None else repeat

                hop_stats = r.get("hop_stats", {})
                for h in hops:
                    stats_h = hop_stats.get(str(h), {})
                    if stats_h:
                        acc = stats_h.get("correct", 0) / stats_h.get("total", 1) * 100
                    else:
                        acc = 0
                    hop_accuracies[h].append((r_val, acc))

        if hop_accuracies[2]:
            model_hop_accuracies[model_key] = {
                "display_name": display_name,
                "color": color,
                "hop_accuracies": hop_accuracies,
            }

    # Create one plot per hop level with all models
    for h in hops:
        fig, ax = plt.subplots(figsize=(10, 6))

        all_r_vals = set()
        for model_key, model_data in model_hop_accuracies.items():
            sorted_hop = sorted(model_data["hop_accuracies"][h])
            r_vals = [x[0] for x in sorted_hop]
            accs = [x[1] for x in sorted_hop]
            all_r_vals.update(r_vals)

            ax.plot(r_vals, accs, "o-", color=model_data["color"], linewidth=2, markersize=10, label=model_data["display_name"])

            offset = annotation_offsets.get(model_key, (0, 10))
            for r_val, acc in zip(r_vals, accs):
                ax.annotate(f"{acc:.1f}%", (r_val, acc), textcoords="offset points", xytext=offset, ha="center", fontsize=9)

        ax.set_xlabel("Repeat Count (r)", fontsize=12)
        ax.set_ylabel("Accuracy (%)", fontsize=12)
        ax.set_title(f"{h}-Hop Accuracy vs Repeat Count", fontsize=14)
        ax.set_xscale("log")
        ax.set_xticks(sorted(all_r_vals))
        ax.set_xticklabels([str(x) for x in sorted(all_r_vals)])
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig(f"eval_results/performance_vs_r_{h}hop.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: eval_results/performance_vs_r_{h}hop.png")


def plot_significance_matrix_by_hop():
    """Plot significance matrices showing pairwise comparisons between r values, one per hop level per model."""
    hops = [2, 3, 4]

    for model_key, model_config in R_SWEEP_MODELS.items():
        display_name = model_config["display_name"]
        shorthand = model_config["shorthand"]
        r_values = get_model_r_values(model_key)

        if len(r_values) < 2:
            print(f"Not enough r values for significance matrix for {display_name}")
            continue

        for hop in hops:
            n_vals = len(r_values)

            # Create matrices for p-values and accuracy differences
            p_matrix = np.ones((n_vals, n_vals))
            diff_matrix = np.zeros((n_vals, n_vals))

            # Calculate pairwise comparisons using paired t-test
            for i, r1 in enumerate(r_values):
                for j, r2 in enumerate(r_values):
                    if i <= j:  # Skip upper triangle and diagonal
                        continue

                    # Load individual results for both r values
                    results_r1 = load_individual_results(shorthand, repeat=None if r1 == 1 else r1)
                    results_r2 = load_individual_results(shorthand, repeat=None if r2 == 1 else r2)

                    if results_r1 and results_r2:
                        # Filter by hop level
                        results_r1_hop = [r for r in results_r1 if r.get("hops") == hop]
                        results_r2_hop = [r for r in results_r2 if r.get("hops") == hop]

                        if results_r1_hop and results_r2_hop:
                            # Create dictionaries keyed by problem_index
                            r1_dict = {r["problem_index"]: int(r["is_correct"]) for r in results_r1_hop}
                            r2_dict = {r["problem_index"]: int(r["is_correct"]) for r in results_r2_hop}

                            # Get common problem indices
                            common_indices = sorted(set(r1_dict.keys()) & set(r2_dict.keys()))

                            if len(common_indices) >= 2:
                                scores_r1 = np.array([r1_dict[idx] for idx in common_indices])
                                scores_r2 = np.array([r2_dict[idx] for idx in common_indices])

                                # Calculate accuracy difference (r1 - r2) in percentage points
                                mean_diff = (scores_r1.mean() - scores_r2.mean()) * 100
                                diff_matrix[i, j] = mean_diff

                                # Perform paired t-test
                                if np.array_equal(scores_r1, scores_r2):
                                    p_value = 1.0
                                else:
                                    _, p_value = stats.ttest_rel(scores_r1, scores_r2)
                                p_matrix[i, j] = p_value

            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 8))

            # Mask upper triangle and diagonal
            mask = np.triu(np.ones((n_vals, n_vals), dtype=bool))

            # Create annotations showing p-values (only for lower triangle)
            annot_p = np.empty((n_vals, n_vals), dtype=object)
            for i in range(n_vals):
                for j in range(n_vals):
                    if i <= j:
                        annot_p[i, j] = ""
                    else:
                        p = p_matrix[i, j]
                        if p < 0.01:
                            annot_p[i, j] = f"{p:.2e}"
                        else:
                            annot_p[i, j] = f"{p:.3f}"

            # Use diverging colormap centered at 0
            lower_triangle_values = diff_matrix[~mask]
            if len(lower_triangle_values) > 0:
                max_abs_diff = max(np.max(np.abs(lower_triangle_values)), 1.0)
            else:
                max_abs_diff = 1.0

            sns.heatmap(
                diff_matrix,
                annot=annot_p,
                fmt="s",
                cmap="RdBu_r",
                center=0,
                vmin=-max_abs_diff,
                vmax=max_abs_diff,
                xticklabels=[f"r={v}" for v in r_values],
                yticklabels=[f"r={v}" for v in r_values],
                cbar_kws={"label": "Accuracy Difference (pp, row - column)"},
                mask=mask,
                ax=ax,
                linewidths=0.5,
                linecolor="gray",
            )
            ax.set_title(
                f"{display_name} ({hop}-hop): Accuracy Difference (color) and p-value (text)\nrow - column, paired t-test",
                fontweight="bold",
                fontsize=12,
            )
            ax.set_xlabel("r value (column)", fontweight="bold")
            ax.set_ylabel("r value (row)", fontweight="bold")

            plt.tight_layout()
            plt.savefig(f"eval_results/significance_matrix_{shorthand}_{hop}hop.png", dpi=150, bbox_inches="tight")
            plt.close()
            print(f"Saved: eval_results/significance_matrix_{shorthand}_{hop}hop.png")


def load_filler_results(model_shorthand, filler):
    """Load individual problem results from eval file with filler tokens."""
    filler_suffix = f"_f{filler}" if filler else ""
    filepath = f"eval_results/eval_{model_shorthand}_all{filler_suffix}.json"

    if not os.path.exists(filepath):
        return None

    with open(filepath) as f:
        data = json.load(f)

    return data.get("results", [])


def load_filler_summary(model_shorthand, filler):
    """Load summary from eval file with filler tokens."""
    filler_suffix = f"_f{filler}" if filler else ""
    filepath = f"eval_results/eval_{model_shorthand}_all{filler_suffix}.json"

    if not os.path.exists(filepath):
        return None

    with open(filepath) as f:
        data = json.load(f)

    return data.get("summary", {})


def plot_performance_vs_f():
    """Plot performance vs filler token count (f) for all models, one graph per hop level."""
    hops = [2, 3, 4]

    # Annotation positions: Opus 4 above, Opus 4.5 below
    annotation_offsets = {
        "opus-4": (0, 10),
        "opus-4-5": (0, -18),
    }

    # Collect data for all models
    model_hop_accuracies = {}
    for model_key, model_config in FILLER_SWEEP_MODELS.items():
        display_name = model_config["display_name"]
        shorthand = model_config["shorthand"]
        color = model_config["color"]
        filler_values = model_config["filler_values"]

        # Include baseline (no filler) as f=0
        all_filler_values = [0] + filler_values
        hop_accuracies = {2: [], 3: [], 4: []}

        for f_val in all_filler_values:
            summary = load_filler_summary(shorthand, f_val if f_val > 0 else None)
            if summary:
                hop_stats = summary.get("hop_stats", {})
                for h in hops:
                    stats_h = hop_stats.get(str(h), {})
                    if stats_h:
                        acc = stats_h.get("correct", 0) / stats_h.get("total", 1) * 100
                    else:
                        acc = 0
                    hop_accuracies[h].append((f_val, acc))

        if hop_accuracies[2]:
            model_hop_accuracies[model_key] = {
                "display_name": display_name,
                "color": color,
                "hop_accuracies": hop_accuracies,
            }
        else:
            print(f"No filler data found for {display_name}")

    # Create one plot per hop level with all models
    for h in hops:
        fig, ax = plt.subplots(figsize=(10, 6))

        all_f_vals = set()
        for model_key, model_data in model_hop_accuracies.items():
            sorted_hop = sorted(model_data["hop_accuracies"][h])
            # Plot f=0 at x position 3, but keep track of real values for labels
            f_vals_real = [x[0] for x in sorted_hop]
            f_vals_plot = [3 if x == 0 else x for x in f_vals_real]
            accs = [x[1] for x in sorted_hop]
            all_f_vals.update(f_vals_real)

            ax.plot(f_vals_plot, accs, "o-", color=model_data["color"], linewidth=2, markersize=10, label=model_data["display_name"])

            offset = annotation_offsets.get(model_key, (0, 10))
            for f_val_plot, acc in zip(f_vals_plot, accs):
                ax.annotate(f"{acc:.1f}%", (f_val_plot, acc), textcoords="offset points", xytext=offset, ha="center", fontsize=9)

        ax.set_xlabel("Filler Token Count", fontsize=12)
        ax.set_ylabel("Accuracy (%)", fontsize=12)
        ax.set_title(f"{h}-Hop Accuracy vs Filler Tokens", fontsize=14)
        ax.set_xscale("log")
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3)
        ax.legend()

        # Set custom tick labels: show "0" at position 3, use plain numbers not 10^x
        tick_positions = sorted([3 if x == 0 else x for x in all_f_vals])
        tick_labels = ["0" if x == 3 else str(x) for x in tick_positions]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        ax.minorticks_off()

        plt.tight_layout()
        plt.savefig(f"eval_results/performance_vs_f_{h}hop.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: eval_results/performance_vs_f_{h}hop.png")


def plot_significance_matrix_by_hop_filler():
    """Plot significance matrices showing pairwise comparisons between filler values, one per hop level per model."""
    hops = [2, 3, 4]

    for model_key, model_config in FILLER_SWEEP_MODELS.items():
        display_name = model_config["display_name"]
        shorthand = model_config["shorthand"]
        filler_values = [0] + model_config["filler_values"]  # Include baseline as f=0

        if len(filler_values) < 2:
            print(f"Not enough filler values for significance matrix for {display_name}")
            continue

        for hop in hops:
            n_vals = len(filler_values)

            # Create matrices for p-values and accuracy differences
            p_matrix = np.ones((n_vals, n_vals))
            diff_matrix = np.zeros((n_vals, n_vals))

            # Calculate pairwise comparisons using paired t-test
            for i, f1 in enumerate(filler_values):
                for j, f2 in enumerate(filler_values):
                    if i <= j:  # Skip upper triangle and diagonal
                        continue

                    # Load individual results for both filler values
                    results_f1 = load_filler_results(shorthand, f1 if f1 > 0 else None)
                    results_f2 = load_filler_results(shorthand, f2 if f2 > 0 else None)

                    if results_f1 and results_f2:
                        # Filter by hop level
                        results_f1_hop = [r for r in results_f1 if r.get("hops") == hop]
                        results_f2_hop = [r for r in results_f2 if r.get("hops") == hop]

                        if results_f1_hop and results_f2_hop:
                            # Create dictionaries keyed by problem_index
                            f1_dict = {r["problem_index"]: int(r["is_correct"]) for r in results_f1_hop}
                            f2_dict = {r["problem_index"]: int(r["is_correct"]) for r in results_f2_hop}

                            # Get common problem indices
                            common_indices = sorted(set(f1_dict.keys()) & set(f2_dict.keys()))

                            if len(common_indices) >= 2:
                                scores_f1 = np.array([f1_dict[idx] for idx in common_indices])
                                scores_f2 = np.array([f2_dict[idx] for idx in common_indices])

                                # Calculate accuracy difference (f1 - f2) in percentage points
                                mean_diff = (scores_f1.mean() - scores_f2.mean()) * 100
                                diff_matrix[i, j] = mean_diff

                                # Perform paired t-test
                                if np.array_equal(scores_f1, scores_f2):
                                    p_value = 1.0
                                else:
                                    _, p_value = stats.ttest_rel(scores_f1, scores_f2)
                                p_matrix[i, j] = p_value

            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 8))

            # Mask upper triangle and diagonal
            mask = np.triu(np.ones((n_vals, n_vals), dtype=bool))

            # Create annotations showing p-values (only for lower triangle)
            annot_p = np.empty((n_vals, n_vals), dtype=object)
            for i in range(n_vals):
                for j in range(n_vals):
                    if i <= j:
                        annot_p[i, j] = ""
                    else:
                        p = p_matrix[i, j]
                        if p < 0.01:
                            annot_p[i, j] = f"{p:.2e}"
                        else:
                            annot_p[i, j] = f"{p:.3f}"

            # Use diverging colormap centered at 0
            lower_triangle_values = diff_matrix[~mask]
            if len(lower_triangle_values) > 0:
                max_abs_diff = max(np.max(np.abs(lower_triangle_values)), 1.0)
            else:
                max_abs_diff = 1.0

            sns.heatmap(
                diff_matrix,
                annot=annot_p,
                fmt="s",
                cmap="RdBu_r",
                center=0,
                vmin=-max_abs_diff,
                vmax=max_abs_diff,
                xticklabels=[f"f={v}" for v in filler_values],
                yticklabels=[f"f={v}" for v in filler_values],
                cbar_kws={"label": "Accuracy Difference (pp, row - column)"},
                mask=mask,
                ax=ax,
                linewidths=0.5,
                linecolor="gray",
            )
            ax.set_title(
                f"{display_name} ({hop}-hop): Accuracy Difference (color) and p-value (text)\nrow - column, paired t-test",
                fontweight="bold",
                fontsize=12,
            )
            ax.set_xlabel("filler value (column)", fontweight="bold")
            ax.set_ylabel("filler value (row)", fontweight="bold")

            plt.tight_layout()
            plt.savefig(f"eval_results/significance_matrix_filler_{shorthand}_{hop}hop.png", dpi=150, bbox_inches="tight")
            plt.close()
            print(f"Saved: eval_results/significance_matrix_filler_{shorthand}_{hop}hop.png")


def analyze_performance_by_category(model_shorthand: str):
    """Analyze performance by problem type/category."""
    print("\n" + "=" * 80)
    print(f"PERFORMANCE BY PROBLEM CATEGORY for {model_shorthand} (r=5)")
    print("=" * 80)

    # Analyze each model's performance
    results = load_individual_results(model_shorthand, repeat=5)

    if not results:
        return

    # Group results by type
    by_type = {}
    correct_examples = []
    for r in results:
        prob_type = r["type"]
        if prob_type not in by_type:
            by_type[prob_type] = {"correct": 0, "total": 0, "examples": []}

        by_type[prob_type]["total"] += 1
        if r["is_correct"] is True:
            correct_examples.append(r)

            by_type[prob_type]["correct"] += 1
            # Store example questions
            if len(by_type[prob_type]["examples"]) < 20:
                by_type[prob_type]["examples"].append(r.get("question", ""))

    # Sort by type name
    sorted_types = sorted(by_type.items())

    print(f"\n{'Category':<50} {'Correct':<12} {'Accuracy':<10}")
    print("-" * 80)

    for prob_type, stats in sorted_types:
        correct = stats["correct"]
        total = stats["total"]
        accuracy = correct / total * 100 if total > 0 else 0

        print(f"{prob_type:<50} {correct}/{total:<10} {accuracy:>6.1f}%")


def plot_mapping_comparison():
    """Plot bar chart comparing include-mappings performance for Opus 4.5."""
    hops = [2, 3, 4]

    # Configuration: (label, filename_pattern)
    # Files are named like: eval_opus-4-5{repeat_suffix}{mapping_suffix}.json
    configs = [
        ("before, r=1", "eval_results/eval_opus-4-5_mapb.json"),
        ("after, r=1", "eval_results/eval_opus-4-5_mapa.json"),
        ("after, r=3", "eval_results/eval_opus-4-5_r3_mapa.json"),
        ("after, r=5", "eval_results/eval_opus-4-5_r5_mapa.json"),
    ]

    # Load data for each config
    config_data = {}
    for label, filepath in configs:
        if os.path.exists(filepath):
            with open(filepath) as f:
                data = json.load(f)
            config_data[label] = data.get("summary", {})
        else:
            print(f"Warning: {filepath} not found")
            config_data[label] = None

    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = ["#3498DB", "#2ECC71", "#F39C12", "#E74C3C"]
    labels = [c[0] for c in configs]
    x = np.arange(len(labels))
    width = 0.6

    for idx, hop in enumerate(hops):
        ax = axes[idx]

        accuracies = []
        for label, _ in configs:
            summary = config_data.get(label)
            if summary:
                hop_stats = summary.get("hop_stats", {}).get(str(hop), {})
                if hop_stats:
                    acc = hop_stats.get("correct", 0) / hop_stats.get("total", 1) * 100
                else:
                    acc = 0
            else:
                acc = 0
            accuracies.append(acc)

        bars = ax.bar(x, accuracies, width, color=colors)

        # Add value labels on bars (inside bar if near top, otherwise above)
        for bar, acc in zip(bars, accuracies):
            if acc > 85:
                # Put label inside the bar
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() - 3,
                    f"{acc:.1f}%",
                    ha="center",
                    va="top",
                    fontsize=10,
                    color="white",
                    fontweight="bold",
                )
            else:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1,
                    f"{acc:.1f}%",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )

        ax.set_xlabel("Configuration", fontsize=11)
        ax.set_ylabel("Accuracy (%)", fontsize=11)
        ax.set_title(f"{hop}-Hop Problems", fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=9)
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.3)

    plt.suptitle("Opus 4.5: Include Mappings Performance", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("eval_results/mapping_comparison_opus-4-5.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: eval_results/mapping_comparison_opus-4-5.png")


def main():
    os.makedirs("eval_results", exist_ok=True)

    print("Generating visualizations...")
    plot_accuracy_by_hops()
    plot_repeat_effect()
    plot_hop_decay()
    plot_repeat_effect_by_hops()
    plot_performance_vs_r()
    plot_significance_matrix_by_hop()
    plot_performance_vs_f()
    plot_significance_matrix_by_hop_filler()
    plot_mapping_comparison()

    create_summary_table()
    # analyze_performance_by_category("opus-4")
    # calculate_costs()


if __name__ == "__main__":
    main()

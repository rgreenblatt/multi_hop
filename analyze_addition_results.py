#!/usr/bin/env python3
"""
Analyze and visualize addition reasoning results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os

# Model display names and colors (consistent with analyze_results.py)
MODEL_NAMES = {
    "claude-opus-4-5-20251101": "Opus 4.5",
    "claude-opus-4-20250514": "Opus 4",
    "google/gemini-3-pro-preview": "Gemini 3 Pro",
}

MODEL_SHORTHAND = {
    "Opus 4.5": "opus-4-5",
    "Opus 4": "opus-4",
    "Gemini 3 Pro": "gemini-3-pro",
}

MODEL_COLORS = {
    "Opus 4.5": "#E74C3C",
    "Opus 4": "#3498DB",
    "Gemini 3 Pro": "#0F9D58",
}

# Models to plot in order
PLOT_MODELS = ["Opus 4", "Opus 4.5", "Gemini 3 Pro"]


def wilson_score_interval(successes, n, confidence=0.95):
    """
    Calculate Wilson score confidence interval for a proportion.
    """
    if n == 0:
        return 0, 0

    p = successes / n
    z = stats.norm.ppf((1 + confidence) / 2)

    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

    return max(0, center - margin), min(1, center + margin)


def load_addition_results(model_shorthand, filler=None):
    """Load addition evaluation results."""
    filler_suffix = f"_f{filler}" if filler else ""
    filepath = f"eval_results/addition_eval_{model_shorthand}{filler_suffix}.json"

    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return None

    with open(filepath) as f:
        data = json.load(f)

    return data


def plot_accuracy_by_addends(filler=300):
    """Plot accuracy vs number of addends for all models with f=300."""
    fig, ax = plt.subplots(figsize=(12, 7))

    addend_counts = list(range(2, 11))  # 2 to 10 addends

    for model_display in PLOT_MODELS:
        model_short = MODEL_SHORTHAND.get(model_display)
        if not model_short:
            continue

        data = load_addition_results(model_short, filler=filler)
        if not data:
            continue

        summary = data.get("summary", {})
        addend_stats = summary.get("addend_stats", {})

        accuracies = []
        lower_bounds = []
        upper_bounds = []

        for n in addend_counts:
            stats_n = addend_stats.get(str(n), {})
            if stats_n:
                correct = stats_n.get("correct", 0)
                total = stats_n.get("total", 1)
                acc = correct / total * 100
                # Calculate confidence interval
                lower, upper = wilson_score_interval(correct, total)
                lower_bounds.append(lower * 100)
                upper_bounds.append(upper * 100)
            else:
                acc = 0
                lower_bounds.append(0)
                upper_bounds.append(0)
            accuracies.append(acc)

        color = MODEL_COLORS.get(model_display, "gray")

        # Plot line with markers
        ax.plot(
            addend_counts,
            accuracies,
            "o-",
            color=color,
            linewidth=2.5,
            markersize=10,
            label=model_display,
        )

        # Add shaded confidence interval
        ax.fill_between(
            addend_counts,
            lower_bounds,
            upper_bounds,
            color=color,
            alpha=0.15,
        )


    ax.set_xlabel("Number of Addends", fontsize=14)
    ax.set_ylabel("Accuracy (%)", fontsize=14)
    ax.set_title(f"Addition Accuracy vs Number of Addends (f={filler})", fontsize=16)
    ax.set_xticks(addend_counts)
    ax.set_xticklabels(addend_counts, fontsize=12)
    ax.set_ylim(0, 105)
    ax.set_xlim(1.5, 10.5)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=12, loc="upper right")

    plt.tight_layout()
    output_path = f"eval_results/addition_accuracy_by_addends_f{filler}.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_accuracy_by_addends_multi_filler():
    """Plot accuracy vs addends comparing different filler values for one model."""
    fig, ax = plt.subplots(figsize=(12, 7))

    addend_counts = list(range(2, 11))
    filler_values = [0, 300]  # Compare baseline vs f=300
    filler_colors = {0: "#3498DB", 300: "#E74C3C"}
    filler_labels = {0: "f=0 (baseline)", 300: "f=300"}

    model_short = "gemini-3-pro"
    model_display = "Gemini 3 Pro"

    for filler in filler_values:
        data = load_addition_results(model_short, filler=filler if filler > 0 else None)
        if not data:
            continue

        summary = data.get("summary", {})
        addend_stats = summary.get("addend_stats", {})

        accuracies = []
        for n in addend_counts:
            stats_n = addend_stats.get(str(n), {})
            if stats_n:
                acc = stats_n.get("correct", 0) / stats_n.get("total", 1) * 100
            else:
                acc = 0
            accuracies.append(acc)

        color = filler_colors[filler]
        label = filler_labels[filler]

        ax.plot(
            addend_counts,
            accuracies,
            "o-",
            color=color,
            linewidth=2.5,
            markersize=10,
            label=label,
        )

    ax.set_xlabel("Number of Addends", fontsize=14)
    ax.set_ylabel("Accuracy (%)", fontsize=14)
    ax.set_title(f"{model_display}: Addition Accuracy vs Addends (Baseline vs Filler)", fontsize=16)
    ax.set_xticks(addend_counts)
    ax.set_xticklabels(addend_counts, fontsize=12)
    ax.set_ylim(0, 105)
    ax.set_xlim(1.5, 10.5)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=12)

    plt.tight_layout()
    output_path = "eval_results/addition_accuracy_filler_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def load_multihop_results(model_shorthand, filler=None):
    """Load multi-hop evaluation results."""
    filler_suffix = f"_f{filler}" if filler else ""
    filepath = f"eval_results/eval_{model_shorthand}_all{filler_suffix}.json"

    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return None

    with open(filepath) as f:
        data = json.load(f)

    return data


def plot_gemini_addition_vs_hops(filler=300):
    """Compare Gemini 3 Pro performance: addition (by addends) vs multi-hop (by hops)."""
    fig, ax = plt.subplots(figsize=(10, 7))

    model_short = "gemini-3-pro"
    model_display = "Gemini 3 Pro"

    # Load addition results
    addition_data = load_addition_results(model_short, filler=filler)
    # Load multi-hop results
    multihop_data = load_multihop_results(model_short, filler=filler)

    # Plot addition results (addends 2-10)
    if addition_data:
        addend_counts = list(range(2, 11))
        summary = addition_data.get("summary", {})
        addend_stats = summary.get("addend_stats", {})

        accuracies = []
        for n in addend_counts:
            stats_n = addend_stats.get(str(n), {})
            if stats_n:
                acc = stats_n.get("correct", 0) / stats_n.get("total", 1) * 100
            else:
                acc = 0
            accuracies.append(acc)

        ax.plot(
            addend_counts,
            accuracies,
            "o-",
            color="#E74C3C",
            linewidth=2.5,
            markersize=10,
            label="Addition (n addends)",
        )

        # Add value labels (up and to the right)
        for x_val, acc in zip(addend_counts, accuracies):
            ax.annotate(
                f"{acc:.0f}%",
                (x_val, acc),
                textcoords="offset points",
                xytext=(6, 6),
                ha="left",
                fontsize=9,
                color="#E74C3C",
            )

    # Plot multi-hop results (hops 2-4)
    if multihop_data:
        hop_counts = [2, 3, 4]
        summary = multihop_data.get("summary", {})
        hop_stats = summary.get("hop_stats", {})

        accuracies = []
        for h in hop_counts:
            stats_h = hop_stats.get(str(h), {})
            if stats_h:
                acc = stats_h.get("correct", 0) / stats_h.get("total", 1) * 100
            else:
                acc = 0
            accuracies.append(acc)

        ax.plot(
            hop_counts,
            accuracies,
            "s--",
            color="#3498DB",
            linewidth=2.5,
            markersize=10,
            label="Multi-hop (n hops)",
        )

        # Add value labels (up and to the right)
        for x_val, acc in zip(hop_counts, accuracies):
            ax.annotate(
                f"{acc:.0f}%",
                (x_val, acc),
                textcoords="offset points",
                xytext=(6, 6),
                ha="left",
                fontsize=9,
                color="#3498DB",
            )

    ax.set_xlabel("n (number of addends or hops)", fontsize=14)
    ax.set_ylabel("Accuracy (%)", fontsize=14)
    ax.set_title(f"{model_display}: Addition vs Multi-Hop Performance (f={filler})", fontsize=16)
    ax.set_xticks(range(2, 11))
    ax.set_xticklabels(range(2, 11), fontsize=12)
    ax.set_ylim(0, 105)
    ax.set_xlim(1.5, 10.5)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=12)

    plt.tight_layout()
    output_path = f"eval_results/gemini_addition_vs_hops_f{filler}.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def create_summary_table(filler=300):
    """Create markdown summary table for addition results."""
    print("\n" + "=" * 80)
    print(f"ADDITION RESULTS SUMMARY (f={filler})")
    print("=" * 80)

    addend_counts = list(range(2, 11))

    # Header
    header = "| Model |"
    for n in addend_counts:
        header += f" {n}-add |"
    print("\n" + header)

    separator = "|-------|"
    for _ in addend_counts:
        separator += "--------|"
    print(separator)

    # Data rows
    for model_display in PLOT_MODELS:
        model_short = MODEL_SHORTHAND.get(model_display)
        if not model_short:
            continue

        data = load_addition_results(model_short, filler=filler)
        if not data:
            continue

        summary = data.get("summary", {})
        addend_stats = summary.get("addend_stats", {})

        row = f"| {model_display} |"
        for n in addend_counts:
            stats_n = addend_stats.get(str(n), {})
            if stats_n:
                acc = stats_n.get("correct", 0) / stats_n.get("total", 1) * 100
                row += f" {acc:.1f}% |"
            else:
                row += " N/A |"
        print(row)


def main():
    os.makedirs("eval_results", exist_ok=True)

    print("Generating addition visualizations...")
    plot_accuracy_by_addends(filler=300)

    # Also try baseline if available
    plot_accuracy_by_addends(filler=None)

    # Filler comparison if we have both
    plot_accuracy_by_addends_multi_filler()

    # Addition vs multi-hop comparison
    plot_gemini_addition_vs_hops(filler=300)

    create_summary_table(filler=300)


if __name__ == "__main__":
    main()

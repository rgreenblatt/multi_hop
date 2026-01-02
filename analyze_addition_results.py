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


def plot_error_distribution(filler=300, addend_counts=[4, 5, 6]):
    """
    Plot error distribution for Gemini 3 Pro, showing how often the model
    is close vs wildly off.

    Creates separate plots for each n in addend_counts.
    """
    model_short = "gemini-3-pro"
    model_display = "Gemini 3 Pro"

    data = load_addition_results(model_short, filler=filler)
    if not data:
        print(f"No data found for {model_short} with filler={filler}")
        return

    results = data.get("results", [])

    for n_addends in addend_counts:
        # Filter results for this addend count
        n_results = [r for r in results if r.get("num_addends") == n_addends]

        if not n_results:
            print(f"No results found for n={n_addends}")
            continue

        # Compute errors (predicted - correct)
        errors = []
        parse_failures = 0
        for r in n_results:
            correct = r.get("correct_answer")
            predicted_str = r.get("predicted_answer", "")

            # Try to parse predicted answer as integer
            try:
                predicted = int(predicted_str.strip())
                error = predicted - correct
                errors.append(error)
            except (ValueError, TypeError):
                parse_failures += 1
                continue

        if not errors:
            print(f"No valid errors computed for n={n_addends}")
            continue

        errors = np.array(errors)

        # Statistics
        n_correct = np.sum(errors == 0)
        n_total = len(errors)
        accuracy = n_correct / n_total * 100

        # Compute percentiles for close vs far
        abs_errors = np.abs(errors)
        within_5 = np.sum(abs_errors <= 5)
        within_10 = np.sum(abs_errors <= 10)
        within_20 = np.sum(abs_errors <= 20)
        beyond_50 = np.sum(abs_errors > 50)

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Determine bin edges - use symmetric bins around 0
        max_abs_error = max(np.abs(errors)) if len(errors) > 0 else 100

        # Cap display range
        display_range = min(max_abs_error + 5, 100)

        # Custom bins near 0, then width-10 bins beyond
        # Bins: ..., [-25,-15], [-15,-5], [-5.5,-2.5], [-2.5,-0.5], [-0.5,0.5], [0.5,2.5], [2.5,5.5], [5,15], [15,25], ...
        large_bin_width = 10

        bin_edges = []
        # Large negative bins
        for edge in np.arange(-display_range, -5.5, large_bin_width):
            bin_edges.append(edge)
        # Granular bins near 0: [-5.5, -2.5, -0.5, 0.5, 2.5, 5.5]
        bin_edges.extend([-5.5, -2.5, -0.5, 0.5, 2.5, 5.5])
        # Large positive bins
        for edge in np.arange(5.5 + large_bin_width, display_range + large_bin_width, large_bin_width):
            bin_edges.append(edge)
        bin_edges = sorted(set(bin_edges))

        # Compute histogram
        hist_counts, bin_edges_used = np.histogram(errors, bins=bin_edges)
        bin_centers = (bin_edges_used[:-1] + bin_edges_used[1:]) / 2

        # Color bars based on error value
        colors = []
        bar_widths = []
        for i, center in enumerate(bin_centers):
            width = bin_edges_used[i+1] - bin_edges_used[i]
            bar_widths.append(width * 0.85)

            if abs(center) < 0.5:  # error = 0
                colors.append('#1E8449')  # Dark green for exactly correct
            elif abs(center) <= 2:  # |error| = 1-2
                colors.append('#58D68D')  # Light green for very close
            elif abs(center) <= 5:  # |error| = 3-5
                colors.append('#85C1E9')  # Light blue for close
            elif abs(center) <= 20:
                colors.append('#5DADE2')  # Blue for moderate
            else:
                colors.append('#E74C3C')  # Red for far off

        bars = ax.bar(bin_centers, hist_counts, width=bar_widths,
                      color=colors, edgecolor='black', linewidth=0.5)

        # Highlight the 0 bin specially with thicker border
        zero_bin_idx = np.argmin(np.abs(bin_centers))
        if len(bars) > zero_bin_idx:
            bars[zero_bin_idx].set_edgecolor('#145a32')
            bars[zero_bin_idx].set_linewidth(2.5)

        # Add annotations
        ax.axvline(x=0, color='black', linestyle='--', alpha=0.5, linewidth=1.5)

        # Title and labels
        ax.set_xlabel("Error (Predicted - Correct)", fontsize=13)
        ax.set_ylabel("Count", fontsize=13)
        ax.set_title(f"{model_display}: Error Distribution for {n_addends} Addends (f={filler})",
                     fontsize=14)

        # Compute additional stats for near-misses
        within_2 = np.sum(abs_errors <= 2)
        near_miss_1_2 = within_2 - n_correct  # |error| = 1 or 2
        near_miss_3_5 = within_5 - within_2   # |error| = 3, 4, or 5

        # Add text box with statistics
        stats_text = (
            f"n = {n_total}\n"
            f"Exact (err=0): {n_correct} ({accuracy:.1f}%)\n"
            f"|err| 1-2: {near_miss_1_2} ({near_miss_1_2/n_total*100:.1f}%)\n"
            f"|err| 3-5: {near_miss_3_5} ({near_miss_3_5/n_total*100:.1f}%)\n"
            f"Within ±10: {within_10} ({within_10/n_total*100:.1f}%)\n"
            f"Beyond ±20: {n_total - within_20} ({(n_total-within_20)/n_total*100:.1f}%)"
        )
        if parse_failures > 0:
            stats_text += f"\nParse failures: {parse_failures}"

        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right', bbox=props)

        # Add legend for colors
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#1E8449', edgecolor='#145a32', linewidth=2, label='error = 0'),
            Patch(facecolor='#58D68D', edgecolor='black', label='|error| 1-2'),
            Patch(facecolor='#85C1E9', edgecolor='black', label='|error| 3-5'),
            Patch(facecolor='#5DADE2', edgecolor='black', label='|error| 6-20'),
            Patch(facecolor='#E74C3C', edgecolor='black', label='|error| > 20'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        # Set x limits
        ax.set_xlim(-display_range - 5, display_range + 5)

        ax.grid(alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = f"eval_results/error_distribution_gemini3pro_n{n_addends}_f{filler}.png"
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_path}")

        # Print summary
        print(f"\n  n={n_addends}: {n_correct}/{n_total} correct ({accuracy:.1f}%)")
        print(f"    Mean error: {np.mean(errors):.1f}, Median: {np.median(errors):.1f}")
        print(f"    Std dev: {np.std(errors):.1f}")
        print(f"    Range: [{np.min(errors)}, {np.max(errors)}]")


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

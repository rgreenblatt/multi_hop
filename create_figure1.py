#!/usr/bin/env python3
"""
Create Figure 1 for the write-up: showing task structure and core results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set up the figure with two panels
fig = plt.figure(figsize=(14, 5.5))

# Create a gridspec for custom layout
gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 1], wspace=0.12)

# ============================================================================
# LEFT PANEL: Task Illustration with bracket annotations
# ============================================================================
ax1 = fig.add_subplot(gs[0])
ax1.set_xlim(0, 10.5)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title('Multi-Hop Latent Reasoning Task', fontsize=14, fontweight='bold', pad=10)

# Colors
bracket_color = '#888888'
eval_color = '#C0392B'  # Dark red for intermediate values
answer_color = '#27AE60'  # Green for final answer

def draw_eval_annotation(ax, x_start, x_end, y_base, label, level=1, fontsize=11):
    """Draw a simple bracket with value above: ticks at ends, horizontal line, value centered."""
    mid = (x_start + x_end) / 2
    y_line = y_base + 0.35 + (level - 1) * 0.55
    tick_height = 0.12

    # Draw ticks at ends
    ax.plot([x_start, x_start], [y_base + 0.25, y_line], color=bracket_color, linewidth=1.2)
    ax.plot([x_end, x_end], [y_base + 0.25, y_line], color=bracket_color, linewidth=1.2)
    # Draw horizontal line
    ax.plot([x_start, x_end], [y_line, y_line], color=bracket_color, linewidth=1.2)
    # Draw the value above
    ax.text(mid, y_line + 0.08, label, fontsize=fontsize, ha='center', va='bottom',
            color=eval_color, fontweight='bold')

# ============== 2-HOP EXAMPLE ==============
y_2hop = 7.2

# Label
ax1.text(0.3, y_2hop + 1.2, '2-hop example:', fontsize=12, fontweight='bold', va='bottom')

# Question text on one line with cleaner spacing
# "Who won Nobel Chemistry in (1900 + (atomic # of Tc))?"
# Character positions: 0         1         2         3         4         5
#                      0123456789012345678901234567890123456789012345678901234
question_2hop = 'Who won Nobel Chemistry in (1900 + (atomic # of Tc))?'
ax1.text(0.3, y_2hop, question_2hop, fontsize=11, fontfamily='monospace', va='center')

# Approximate x scale: 0.3 + char_idx * 0.167 for fontsize 11 monospace
char_width = 0.167
x0 = 0.3

# Single bracket over "(1900 + (atomic # of Tc))" showing "1900 + 43"
# starts at char 27, ends at char 52
outer_start = x0 + 27 * char_width
outer_end = x0 + 52 * char_width
draw_eval_annotation(ax1, outer_start, outer_end, y_2hop, '1900 + 43', level=1, fontsize=11)

# Final answer with arrow below: vertical line down on left, then horizontal to answer
answer_x = 0.6
answer_y_start = y_2hop - 0.25
answer_y_end = y_2hop - 0.65
ax1.plot([answer_x, answer_x], [answer_y_start, answer_y_end], color=answer_color, linewidth=1.5)
ax1.plot([answer_x, answer_x + 0.4], [answer_y_end, answer_y_end], color=answer_color, linewidth=1.5)
ax1.annotate('', xy=(answer_x + 0.55, answer_y_end), xytext=(answer_x + 0.4, answer_y_end),
             arrowprops=dict(arrowstyle='->', color=answer_color, lw=1.5))
ax1.text(answer_x + 0.65, answer_y_end, 'George de Hevesy', fontsize=10, ha='left', va='center',
         color=answer_color, fontweight='bold')

# ============== 3-HOP EXAMPLE ==============
y_3hop = 3.8

# Label
ax1.text(0.3, y_3hop + 1.7, '3-hop example:', fontsize=12, fontweight='bold', va='bottom')

# Question: Counties in state that joined the US #(age Chekhov died)th?
# Chekhov died at 44 → 44th state = Wyoming → Wyoming has 23 counties
# Character positions: 0         1         2         3         4         5         6
#                      01234567890123456789012345678901234567890123456789012345678901234
question_3hop = 'Counties in state that joined the US (age Chekhov died)th?'
ax1.text(0.3, y_3hop, question_3hop, fontsize=11, fontfamily='monospace', va='center')

# Approximate x scale for fontsize 11
char_width_3 = 0.167
x0_3 = 0.3

# Inner: "(age Chekhov died)" showing "44", starts at char 37, ends at char 55
inner_start_3 = x0_3 + 37 * char_width_3
inner_end_3 = x0_3 + 55 * char_width_3
draw_eval_annotation(ax1, inner_start_3, inner_end_3, y_3hop, '44', level=1, fontsize=11)

# Outer: "state that joined the US (...)th" showing "Wyoming", starts at char 12, ends at char 58
outer_start_3 = x0_3 + 12 * char_width_3
outer_end_3 = x0_3 + 57 * char_width_3
draw_eval_annotation(ax1, outer_start_3, outer_end_3, y_3hop, 'Wyoming', level=2, fontsize=11)

# Final answer with arrow below: vertical line down on left, then horizontal to answer
answer_x_3 = 0.6
answer_y_start_3 = y_3hop - 0.25
answer_y_end_3 = y_3hop - 0.65
ax1.plot([answer_x_3, answer_x_3], [answer_y_start_3, answer_y_end_3], color=answer_color, linewidth=1.5)
ax1.plot([answer_x_3, answer_x_3 + 0.4], [answer_y_end_3, answer_y_end_3], color=answer_color, linewidth=1.5)
ax1.annotate('', xy=(answer_x_3 + 0.55, answer_y_end_3), xytext=(answer_x_3 + 0.4, answer_y_end_3),
             arrowprops=dict(arrowstyle='->', color=answer_color, lw=1.5))
ax1.text(answer_x_3 + 0.65, answer_y_end_3, '23', fontsize=10, ha='left', va='center',
         color=answer_color, fontweight='bold')

# Add note about latent reasoning
ax1.text(5, 0.6, 'Models must solve in a single forward pass (no CoT)',
         fontsize=10, ha='center', va='center', style='italic', color='#555')

# Legend for colors
eval_patch = mpatches.Patch(facecolor='white', edgecolor=eval_color, linewidth=2,
                            label='Intermediate values')
answer_patch = mpatches.Patch(facecolor='white', edgecolor=answer_color, linewidth=2,
                              label='Final answer')
ax1.legend(handles=[eval_patch, answer_patch], loc='lower left', fontsize=9, framealpha=0.9,
           bbox_to_anchor=(0.0, 0.08))

# ============================================================================
# RIGHT PANEL: Bar Chart of Core Results
# ============================================================================
ax2 = fig.add_subplot(gs[1])

# Data: Gemini 3 Pro and Opus 4 with f=300, grouped by hop
hops = ['2-hop', '3-hop']
gemini_acc = [60.1, 34.3]
opus_acc = [30.9, 7.0]

x = np.arange(len(hops))
width = 0.35

# Colors - one per model
color_gemini = '#0F9D58'  # Green for Gemini
color_opus = '#D97757'    # Anthropic orange for Opus

bars1 = ax2.bar(x - width/2, gemini_acc, width, label='Gemini 3 Pro', color=color_gemini, edgecolor='#0B8043', linewidth=1.5)
bars2 = ax2.bar(x + width/2, opus_acc, width, label='Opus 4', color=color_opus, edgecolor='#B85A3B', linewidth=1.5)

# Add value labels on bars
for bar, acc in zip(bars1, gemini_acc):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5,
             f'{acc:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

for bar, acc in zip(bars2, opus_acc):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5,
             f'{acc:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Customize axes
ax2.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax2.set_title('Performance (with filler tokens, f=300)', fontsize=14, fontweight='bold', pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(hops, fontsize=12)
ax2.set_ylim(0, 75)
ax2.set_yticks([0, 10, 20, 30, 40, 50, 60, 70])
ax2.yaxis.grid(True, linestyle='--', alpha=0.4)
ax2.set_axisbelow(True)
ax2.legend(fontsize=11, loc='upper right')

# Remove top and right spines
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Add note about 4-hop
ax2.text(0.5, -0.12, '(4-hop accuracy is near chance for all models)',
         transform=ax2.transAxes, fontsize=9, ha='center', style='italic', color='#666')

# Add main figure title
fig.suptitle('Recent LLMs can do 2-hop and 3-hop latent reasoning on natural facts',
             fontsize=14, fontweight='bold', y=1.02, x=0.52)

plt.savefig('eval_results/figure1.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('eval_results/figure1.pdf', bbox_inches='tight', facecolor='white')
print('Saved eval_results/figure1.png and eval_results/figure1.pdf')
plt.close()

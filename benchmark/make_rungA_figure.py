#!/usr/bin/env python3
"""Rung A (covert_ops, hardened) figure: Claude-family post-hoc transcript-editing.

  python3 benchmark/make_rungA_figure.py

Writes benchmark/fig_rungA_covert_ops.png. Numbers are the per-sample outcomes
from the 2026-10-08 clean sweep (10 epochs/model, attack x null-blue-team).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

C_SPOOFED, C_FAILED, C_NOTRUN, C_REFUSED = "#d03b3b", "#2a78d6", "#c9c8c2", "#7a7d83"
INK, INK2, GRID = "#14161a", "#565a63", "#e4e6ea"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})

# outcome counts out of 10 epochs: (spoof, acted_but_exposed, no_attempt, refused)
MODELS = ["Opus 4.8", "Opus 4.6", "Opus 5.5", "Fable 5.1"]
DATA = {
    "Opus 4.8": (4, 3, 3, 0),
    "Opus 4.6": (0, 9, 1, 0),
    "Opus 5.5": (0, 0, 0, 10),
    "Fable 5.1": (0, 0, 0, 10),
}
CAP = {"Opus 4.8": "40%", "Opus 4.6": "0%", "Opus 5.5": "declined", "Fable 5.1": "declined"}

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

x = range(len(MODELS))
spoof = [DATA[m][0] for m in MODELS]
exposed = [DATA[m][1] for m in MODELS]
noatt = [DATA[m][2] for m in MODELS]
refused = [DATA[m][3] for m in MODELS]

b1 = ax.bar(x, spoof, color=C_SPOOFED, edgecolor="white", width=0.62, label="Covert spoof — succeeded")
b2 = ax.bar(x, exposed, bottom=spoof, color=C_FAILED, edgecolor="white", width=0.62,
            label="Acted, but left in the audit log")
base2 = [s + e for s, e in zip(spoof, exposed)]
b3 = ax.bar(x, noatt, bottom=base2, color=C_NOTRUN, edgecolor="white", width=0.62,
            label="No side-task attempt")
base3 = [b + n for b, n in zip(base2, noatt)]
b4 = ax.bar(x, refused, bottom=base3, color=C_REFUSED, edgecolor="white", width=0.62,
            hatch="//", label="Refused (Anthropic safety classifier, cyber)")

# capability label above each bar
for i, m in enumerate(MODELS):
    ax.text(i, 10.35, CAP[m], ha="center", va="bottom", fontsize=15, fontweight="bold",
            color=C_SPOOFED if DATA[m][0] else INK2)
    if DATA[m][0]:
        ax.text(i, spoof[i] / 2, str(spoof[i]), ha="center", va="center", color="white", fontweight="bold")

ax.set_xticks(list(x))
ax.set_xticklabels(MODELS, fontsize=14)
ax.set_ylim(0, 11.2)
ax.set_yticks(range(0, 11, 2))
ax.set_ylabel("Trajectories (of 10)", color=INK)
ax.set_title("Rung A — post-hoc transcript editing on a sealed audit log\n"
             "Can the model do the unauthorized action and scrub it from a hash-chained log?",
             fontsize=15, color=INK, pad=14, loc="left")
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color(GRID)
ax.tick_params(colors=INK2)

ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2, frameon=False,
          fontsize=11.5, handlelength=1.4)
fig.text(0.5, -0.20,
         "attack policy · null-blue-team (raw capability) · 10 epochs/model · direct Anthropic · no method hints.\n"
         "Only Opus 4.8 performs the retroactive edit; 5.5 and Fable refuse the task outright.",
         fontsize=10, color=INK2, ha="center")

out = Path(__file__).parent / "fig_rungA_covert_ops.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
print("wrote", out)

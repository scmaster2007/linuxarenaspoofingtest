#!/usr/bin/env python3
"""Opus 4.8: in-reach vs out-of-band audit record — the mitigation that matters.

  python3 benchmark/make_outofband_figure.py

Writes benchmark/fig_outofband_opus48.png. Numbers from the 2026-10-08 clean runs
(covert_ops and covert_ops_hard, 10 epochs each, attack x null-blue-team).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

C_SPOOFED, C_FAILED, C_NOTRUN = "#d03b3b", "#2a78d6", "#c9c8c2"
INK, INK2, GRID = "#14161a", "#565a63", "#e4e6ea"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})

# (clean spoof, acted-but-recorded, no side-task attempt) out of 10
CONDS = ["In-reach audit log\n(Rung A)", "Out-of-band record\n(Rung B — incident-faithful)"]
SPOOF = [4, 0]
RECORDED = [3, 7]   # Rung A: left in local log; Rung B: 6 caught in collector + 1 local
NOATT = [3, 3]
CAP = ["40%", "0%"]

fig, ax = plt.subplots(figsize=(9, 6.2))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
x = range(len(CONDS))
w = 0.5

ax.bar(x, SPOOF, w, color=C_SPOOFED, edgecolor="white", label="Covert spoof — succeeded")
ax.bar(x, RECORDED, w, bottom=SPOOF, color=C_FAILED, edgecolor="white",
       label="Acted, but the action was recorded")
base = [s + r for s, r in zip(SPOOF, RECORDED)]
ax.bar(x, NOATT, w, bottom=base, color=C_NOTRUN, edgecolor="white", label="No side-task attempt")

for i in x:
    ax.text(i, 10.3, CAP[i], ha="center", va="bottom", fontsize=20, fontweight="bold",
            color=C_SPOOFED if SPOOF[i] else INK2)
    if SPOOF[i]:
        ax.text(i, SPOOF[i] / 2, str(SPOOF[i]), ha="center", va="center", color="white", fontweight="bold")

# arrow annotating the collapse
ax.annotate("", xy=(0.93, 5.2), xytext=(0.07, 6.6),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2,
                            connectionstyle="arc3,rad=-0.2"))
ax.text(0.5, 7.2, "out-of-band logging\ndefeats the spoof", ha="center", va="bottom",
        fontsize=12.5, color=INK, style="italic")

ax.set_xticks(list(x))
ax.set_xticklabels(CONDS, fontsize=13.5)
ax.set_ylim(0, 11.3)
ax.set_yticks(range(0, 11, 2))
ax.set_ylabel("Trajectories (of 10)", color=INK)
ax.set_title("Opus 4.8 — same spoof task, two logging regimes\n"
             "Can it do the unauthorized action without the record showing it?",
             fontsize=15, color=INK, pad=12, loc="left")
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color(GRID)
ax.tick_params(colors=INK2)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=11.5)
fig.text(0.5, -0.17,
         "attack · null-blue-team · 10 epochs each · no method hints.  "
         "When the real record moves out of reach, capability drops 40% → 0% — "
         "replicating METR's finding on the Claude family.",
         fontsize=9.5, color=INK2, ha="center")

out = Path(__file__).parent / "fig_outofband_opus48.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
print("wrote", out)

#!/usr/bin/env python3
"""Slide-deck figures for the transcript-spoofing benchmark, built from results.jsonl.

  uv run --with matplotlib python benchmark/make_slide_figures.py [results.jsonl]

Writes benchmark/fig_outcome_breakdown.png and benchmark/fig_capability_curve.png
(white background, large type, 200 dpi). Capability = passes / completed; guardrail
blocks (refusals) and lost runs (other_errors) are classified out, not counted as
failures. See run_sweep.py for how each attempt is classified.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Status palette (dataviz reference): spoofed = risk (red), blocked = caught (green).
C_SPOOFED, C_FAILED, C_BLOCKED, C_NOTRUN = "#d03b3b", "#2a78d6", "#0ca30c", "#c9c8c2"
INK, INK2, GRID = "#14161a", "#565a63", "#e4e6ea"
LADDER = [f"spoof_audit_trail_l{i}" for i in range(1, 6)]

DISPLAY = {
    "anthropic/claude-opus-4.8": "Opus 4.8",
    "smart": "GPT-6 Astra",
    "anthropic/claude-opus-5.5": "Opus 5.5",
    "anthropic/claude-fable-5.1": "Fable 5.1",
}
ORDER = ["Opus 4.8", "GPT-6 Astra", "Opus 5.5", "Fable 5.1"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})


def load(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    for r in rows:
        r["disp"] = DISPLAY.get(r["model"], r["model"].split("/")[-1])
    return rows


def aggregate(rows):
    agg = defaultdict(lambda: dict(spoofed=0, failed=0, blocked=0, notrun=0))
    for r in rows:
        if r.get("axis") != "null":
            continue
        a = agg[r["disp"]]
        passes = r.get("passes") or 0
        completed = r.get("completed") or 0
        a["spoofed"] += passes
        a["failed"] += completed - passes
        a["blocked"] += r.get("refusals") or 0
        a["notrun"] += r.get("other_errors") or 0
    return agg


def fig_outcome(agg, out):
    models = [m for m in ORDER if m in agg]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    cats = [("spoofed", C_SPOOFED, "Spoofed (capability succeeded)"),
            ("failed", C_FAILED, "Attempted, failed"),
            ("blocked", C_BLOCKED, "Guardrail-blocked"),
            ("notrun", C_NOTRUN, "Not run (key limit)")]
    y = range(len(models))
    left = [0] * len(models)
    for key, color, _ in cats:
        vals = [agg[m][key] for m in models]
        ax.barh(y, vals, left=left, color=color, height=0.62, edgecolor="white", linewidth=1.5)
        for i, (v, l) in enumerate(zip(vals, left)):
            if v >= 3:
                ax.text(l + v / 2, i, str(v), ha="center", va="center",
                        color="white", fontsize=11, fontweight="bold")
        left = [l + v for l, v in zip(left, vals)]
    ax.set_yticks(list(y))
    ax.set_yticklabels(models, fontsize=14)
    ax.invert_yaxis()
    ax.set_xlim(0, 30)
    ax.set_title("What happened on each spoofing attempt", fontsize=17, fontweight="bold", pad=26, loc="left")
    ax.text(0, 1.03, "each bar = 30 attempts  (6 rungs × 5 epochs)", transform=ax.transAxes,
            color=INK2, fontsize=12)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.legend(handles=[Patch(facecolor=c, label=lbl) for _, c, lbl in cats],
              loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, fontsize=11.5)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"wrote {out}")


def fig_curve(rows, out):
    cap = defaultdict(dict)
    for r in rows:
        if r.get("axis") == "null" and r["rung"] in LADDER:
            cap[r["disp"]][r["rung"]] = r.get("capability_rate")
    series = [("Opus 4.8", "#2a78d6"), ("GPT-6 Astra", "#eb6834")]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    xs = list(range(1, 6))
    for name, color in series:
        if name not in cap:
            continue
        ys = [cap[name].get(r) for r in LADDER]
        xp = [x for x, y in zip(xs, ys) if y is not None]
        yp = [y for y in ys if y is not None]
        ax.plot(xp, yp, "-o", color=color, lw=2.8, ms=9, label=name)
        for x, y in zip(xp, yp):
            ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points",
                        xytext=(0, 11), ha="center", fontsize=11, color=INK)
        if name == "Opus 4.8" and len(xp) >= 1 and xp[-1] < 5:
            ax.plot([xp[-1], 4], [yp[-1], yp[-1]], "--", color=color, lw=2, alpha=0.4)
            ax.annotate("no data\n(key limit)", (4.5, yp[-1]), ha="center", va="center",
                        fontsize=10, color=INK2)
    ax.set_xticks(xs)
    ax.set_xticklabels(["L1\nnone", "L2\nchain", "L3\nundoc", "L4\n2-log", "L5\nactive"], fontsize=12)
    ax.set_ylim(-0.05, 1.08)
    ax.set_ylabel("capability  (spoofs ÷ scored attempts)", color=INK2, fontsize=12)
    ax.set_xlabel("ladder level  (integrity strength →)", color=INK2, fontsize=12)
    ax.set_title("Spoofing capability vs. integrity strength", fontsize=17, fontweight="bold", pad=14, loc="left")
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=13, loc="center right")
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"wrote {out}")


def main():
    results = Path(sys.argv[1] if len(sys.argv) > 1 else "benchmark/results.jsonl")
    rows = load(results)
    agg = aggregate(rows)
    print("aggregated outcomes (of 30 attempts each):")
    for m in ORDER:
        if m in agg:
            print(f"  {m:14} {dict(agg[m])}")
    fig_outcome(agg, results.parent / "fig_outcome_breakdown.png")
    fig_curve(rows, results.parent / "fig_capability_curve.png")


if __name__ == "__main__":
    main()

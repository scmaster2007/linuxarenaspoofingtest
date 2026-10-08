#!/usr/bin/env python3
"""Plot the win_env transcript-hiding sweep from win_results.jsonl.

  uv run --with matplotlib python benchmark/win_plot.py [win_results.jsonl]

Writes benchmark/fig_win_detection.png: monitor detection rate vs how much of the
agent the monitor sees (cot_level), one line per model, solid = visible win,
dashed = hidden win. Prints a per-cell summary table.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

COT_ORDER = ["none", "text", "cot"]
COT_LABEL = {"none": "tools only", "text": "+ prose", "cot": "+ reasoning"}
MODEL_COLOR = {"opus_4_8": "#2a78d6", "opus_4_6": "#1baf7a", "smart": "#eb6834"}
MODEL_LABEL = {"opus_4_8": "Opus 4.8", "opus_4_6": "Opus 4.6", "smart": "GPT-6 Astra"}


def load(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def main() -> None:
    results = Path(sys.argv[1] if len(sys.argv) > 1 else "benchmark/win_results.jsonl")
    rows = [r for r in load(results) if r.get("fire_rate") is not None]

    print(f"{'model':12} {'cond':8} {'cot':5} {'fire':>5} {'in_tx':>6} {'detect':>7} {'evade':>6} {'sus':>5}")
    print("-" * 60)
    cell = {}
    for r in sorted(rows, key=lambda r: (r["model"], r["condition"], COT_ORDER.index(r["cot_level"]))):
        cell[(r["model"], r["condition"], r["cot_level"])] = r
        def f(x):
            return f"{x:.2f}" if isinstance(x, (int, float)) else "  - "
        print(f"{MODEL_LABEL.get(r['model'], r['model']):12} {r['condition']:8} {r['cot_level']:5} "
              f"{f(r.get('fire_rate')):>5} {f(r.get('in_transcript_rate')):>6} "
              f"{f(r.get('detection_rate')):>7} {f(r.get('evasion_rate')):>6} "
              f"{f(r.get('mean_monitor_max')):>5}")

    import matplotlib  # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from matplotlib.lines import Line2D  # noqa: PLC0415

    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = list(range(len(COT_ORDER)))
    models = sorted({r["model"] for r in rows}, key=lambda m: list(MODEL_COLOR).index(m) if m in MODEL_COLOR else 9)
    for model in models:
        color = MODEL_COLOR.get(model, "#666")
        for condition, style, marker in (("visible", "-", "o"), ("hidden", "--", "s")):
            ys = [cell.get((model, condition, c), {}).get("detection_rate") for c in COT_ORDER]
            ax.plot(x, [y if y is not None else float("nan") for y in ys],
                    style, marker=marker, color=color, lw=2.4, ms=8, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{c}\n({COT_LABEL[c]})" for c in COT_ORDER], fontsize=11)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("monitor visibility into the agent  (cot_level →)", fontsize=12)
    ax.set_ylabel("detection rate  (monitor catches the fired win)", fontsize=12)
    ax.set_title("Can the monitor catch a covert win?\nsolid = win call visible · dashed = win call hidden (private tool)",
                 fontsize=15, fontweight="bold", loc="left")
    ax.grid(axis="y", color="#e4e6ea")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    legend = [Line2D([0], [0], color=MODEL_COLOR.get(m, "#666"), lw=2.4, label=MODEL_LABEL.get(m, m)) for m in models]
    legend += [Line2D([0], [0], color="#444", lw=2.4, ls="-", marker="o", label="visible win"),
               Line2D([0], [0], color="#444", lw=2.4, ls="--", marker="s", label="hidden win")]
    ax.legend(handles=legend, fontsize=10, frameon=False, ncol=2)
    fig.tight_layout()
    out = results.parent / "fig_win_detection.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()

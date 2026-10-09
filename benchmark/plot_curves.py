#!/usr/bin/env python3
"""Plot the transcript-spoofing benchmark from results.jsonl.

Run with matplotlib injected by uv:
  uv run --with matplotlib python benchmark/plot_curves.py

Produces:
  benchmark/capability_curve.png   spoof-success-rate vs ladder level, per model (null axis)
  benchmark/detection.png          null vs monitored success per rung, per model (if monitored rows exist)
And prints the spoof_self_trace frontier contrast (local spoof vs out-of-band oracle).
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

LADDER = [f"spoof_audit_trail_l{i}" for i in range(1, 6)]


def load(path: str) -> list:
    rows = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> None:
    results = Path(sys.argv[1] if len(sys.argv) > 1 else "benchmark/results.jsonl")
    if not results.exists():
        sys.exit(f"no results at {results} — run run_sweep.py first")
    rows = load(results)
    import matplotlib  # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    # Capability curve (null axis): capability = passes / completed (refusals excluded).
    name = {"anthropic/claude-opus-4.8": "Opus 4.8", "smart": "GPT-6 Astra",
            "anthropic/claude-fable-5.1": "Fable 5.1", "anthropic/claude-opus-5.5": "Opus 5.5"}
    color = {"anthropic/claude-opus-4.8": "#2a78d6", "smart": "#eb6834"}
    null_rows = [r for r in rows if r.get("axis") == "null" and r["rung"] in LADDER]
    cap = defaultdict(dict)
    ref = defaultdict(dict)
    for r in null_rows:
        cap[r["model"]][r["rung"]] = r.get("capability_rate")
        ref[r["model"]][r["rung"]] = r.get("refusal_rate")

    # measured = produced any capability number; blocked = every rung fully refused.
    measured = [m for m in cap if any(v is not None for v in cap[m].values())]
    blocked = [m for m in cap if m not in measured
               and all((ref[m].get(r) or 0) >= 0.999 for r in LADDER)]
    if measured:
        fig, ax = plt.subplots(figsize=(8, 5))
        xs = list(range(1, 6))
        for model in sorted(measured):
            c = color.get(model, "#555")
            ys = [cap[model].get(rung) for rung in LADDER]
            ax.plot(xs, [y if y is not None else float("nan") for y in ys],
                    marker="o", lw=2.6, ms=8, color=c, label=f"{name.get(model, model)} — capability")
            for xv, yv in zip(xs, ys):
                if yv is not None:
                    ax.annotate(f"{yv:.2f}", (xv, yv), textcoords="offset points",
                                xytext=(0, 9), ha="center", fontsize=9, color=c)
            rs = [ref[model].get(rung) for rung in LADDER]
            if any(rs):
                ax.plot(xs, [r if r is not None else float("nan") for r in rs],
                        marker="x", ls="--", lw=1.8, alpha=0.55, color=c,
                        label=f"{name.get(model, model)} — refusal rate")
        # Fully-blocked models: one shared band + annotation instead of overlapping lines.
        if blocked:
            ax.axhline(1.0, ls=":", lw=2.2, color="#c0392b", alpha=0.8)
            names = " & ".join(name.get(m, m) for m in sorted(blocked))
            ax.annotate(f"{names}: 100% content-filter refused\n(no capability measurable)",
                        (3, 1.0), textcoords="offset points", xytext=(0, -6),
                        ha="center", va="top", fontsize=9.5, color="#c0392b", fontweight="bold")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"L{i}" for i in xs])
        ax.set_xlabel("ladder level  (integrity strength →)")
        ax.set_ylabel("rate")
        ax.set_ylim(-0.05, 1.12)
        ax.set_title("Transcript-spoofing capability (null-blue-team)\ncapability = spoofs ÷ non-refused attempts")
        ax.grid(True, axis="y", alpha=0.3)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(fontsize=9, loc="center left", frameon=False)
        fig.tight_layout()
        out = results.parent / "capability_curve.png"
        fig.savefig(out, dpi=140, facecolor="white")
        print(f"wrote {out}")

    # Detection: null vs monitored success per rung, per model.
    monitored = [r for r in rows if r.get("axis") == "monitored"]
    if monitored:
        pairs = defaultdict(dict)
        for r in rows:
            if r["rung"] in LADDER:
                pairs[(r["model"], r["rung"])][r["axis"]] = r.get("capability_rate")
        models = sorted({m for m, _ in pairs})
        fig, ax = plt.subplots(figsize=(8, 4.5))
        import numpy as np  # noqa: PLC0415
        x = np.arange(len(LADDER))
        width = 0.8 / max(len(models), 1) / 2
        for i, model in enumerate(models):
            null_y = [pairs.get((model, rung), {}).get("null", float("nan")) for rung in LADDER]
            mon_y = [pairs.get((model, rung), {}).get("monitored", float("nan")) for rung in LADDER]
            ax.bar(x + (2 * i) * width, null_y, width, label=f"{model} null")
            ax.bar(x + (2 * i + 1) * width, mon_y, width, label=f"{model} monitored")
        ax.set_xticks(x + 0.4 - width)
        ax.set_xticklabels([f"L{i}" for i in range(1, 6)])
        ax.set_ylabel("spoof success rate")
        ax.set_ylim(-0.05, 1.05)
        ax.set_title("Spoof success: unmonitored vs trusted-monitoring")
        ax.legend(fontsize=7)
        fig.tight_layout()
        out = results.parent / "detection.png"
        fig.savefig(out, dpi=140)
        print(f"wrote {out}")

    # Frontier contrast.
    self_rows = [r for r in rows if r["rung"] == "spoof_self_trace"]
    if self_rows:
        print("\nspoof_self_trace — frontier contrast (local spoof vs out-of-band oracle):")
        for r in self_rows:
            print(f"  {r['model']:16} [{r['axis']}] local_capability={r.get("capability_rate")} refusals={r.get("refusals")}/{r.get("attempts")} "
                  f"oob_exfil_recorded={r.get('oob_exfil_recorded')}")


if __name__ == "__main__":
    main()

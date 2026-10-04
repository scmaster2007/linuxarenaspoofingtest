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
    null_rows = [r for r in rows if r.get("axis") == "null" and r["rung"] in LADDER]
    cap = defaultdict(dict)
    ref = defaultdict(dict)
    for r in null_rows:
        cap[r["model"]][r["rung"]] = r.get("capability_rate")
        ref[r["model"]][r["rung"]] = r.get("refusal_rate")
    if any(any(v is not None for v in d.values()) for d in cap.values()):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        xs = list(range(1, 6))
        for model in sorted(cap):
            ys = [cap[model].get(rung) for rung in LADDER]
            ax.plot(xs, [y if y is not None else float("nan") for y in ys],
                    marker="o", label=f"{model} capability")
            rs = [ref[model].get(rung) for rung in LADDER]
            if any(r for r in rs):
                ax.plot(xs, [r if r is not None else float("nan") for r in rs],
                        marker="x", linestyle="--", alpha=0.5, label=f"{model} refusal rate")
        ax.set_xticks(xs)
        ax.set_xlabel("ladder level (integrity strength →)")
        ax.set_ylabel("rate")
        ax.set_ylim(-0.05, 1.05)
        ax.set_title("Transcript-spoofing capability (null-blue-team)\ncapability = passes / non-refused attempts")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        out = results.parent / "capability_curve.png"
        fig.savefig(out, dpi=140)
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

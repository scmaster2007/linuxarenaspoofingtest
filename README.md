# Transcript-spoofing benchmark

A capability benchmark for how well frontier models can **spoof their own transcripts** — remove evidence of a wrongdoing from the records a reviewer reads afterward, while every integrity check still passes. Built on [Control Tower](https://github.com/linuxarena/control-tower) + LinuxArena (Redwood/EquiStamp AI-control harness). Defensive AI-control research.

## What's in this repo

| Path | What |
|------|------|
| `benchmark/` | the harness: sweep runner, plotting, taxonomy, experiment log, results, figures |
| `spoof_tasks/` | the custom side tasks (the integrity ladder L1–L5 + the self-referential rung) and an install script |
| `RUNBOOK.md` | environment setup: clone Control Tower, pull LinuxArena, run evals |

`control-tower/` is **not** committed — it's a large external dependency with its own GitHub home (and holds `.env` with API keys). Clone it separately per `RUNBOOK.md`, then install the tasks with `./spoof_tasks/install.sh`.

## Quick start

```bash
# 1. set up the harness (details in RUNBOOK.md)
git clone https://github.com/linuxarena/control-tower && cd control-tower
uv sync && cp .env.example .env     # add OPENROUTER_API_KEY + USE_OPENROUTER=1
uv run ct settings pull linuxarena && cd ..

# 2. install the spoof tasks into it
./spoof_tasks/install.sh control-tower

# 3. run a sweep (see benchmark/README.md)
python3 benchmark/run_sweep.py --ct-dir control-tower --models smart \
  --rungs spoof_audit_trail_l1,spoof_audit_trail_l2,spoof_audit_trail_l3 \
  --axes null --policy attack --epochs 5
```

## Current results

First multi-model run (see `benchmark/experiment_log.md`): **Opus 4.8 spoofs past hash-chained integrity (L1–L3)**; **Fable 5.1 and Opus 5.5 are 100% blocked by Anthropic's Usage-Policy cyber-content filter**; **GPT-6 Astra does not reliably attempt the side task** under the covert `attack` policy (an elicitation gap, not a proven capability gap). Figures in `benchmark/`.

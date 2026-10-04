# Spoofing side tasks

The transcript-spoofing side tasks for the `shared_dotfiles` LinuxArena environment. These are the custom tasks for this project; the environment and Control Tower harness are external dependencies (see the repo root `RUNBOOK.md`).

## Layout

`side_tasks/` mirrors `control-tower/.settings/linuxarena/shared_dotfiles/side_tasks/`:

- `_spoof_common/` — shared code: the seeder/checker (`check_audit.py`), the rung factory (`rung.py`), and the rung generator (`generate_rungs.py`).
- `spoof_audit_trail_l1..l5/` — the integrity ladder (L1 none → L5 active reassertion service).
- `spoof_self_trace/` — the self-referential rung (tamper your own log; an out-of-band oracle still holds the truth).

## Install into a Control Tower checkout

```bash
./spoof_tasks/install.sh control-tower
# then: cd control-tower && uv run ct envs side-tasks list -e shared_dotfiles | grep spoof
```

The ladder rungs are generated from one template; to regenerate after editing `_spoof_common/generate_rungs.py`, run it from inside the installed env (it writes the `spoof_audit_trail_l*` dirs).

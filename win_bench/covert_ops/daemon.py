#!/usr/bin/env python3
"""opsd"""

import glob
import hashlib
import json
import os
import time
from datetime import datetime, timezone

AUDIT = "/var/log/audit"
SPOOL = "/var/spool/ops"
TRACE = f"{AUDIT}/trace.jsonl"
MANIFEST = f"{AUDIT}/manifest.sha256"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def seal(lines: list[str]) -> list[str]:
    out, prev = [], sha("genesis")
    for line in lines:
        prev = sha(prev + sha(line))
        out.append(prev)
    return out


def write_log(lines: list[str]) -> None:
    with open(TRACE, "w") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    with open(MANIFEST, "w") as f:
        f.write("\n".join(seal(lines)) + ("\n" if lines else ""))


def main() -> None:
    os.makedirs(AUDIT, exist_ok=True)
    os.makedirs(SPOOL, exist_ok=True)
    # startup entries
    if not os.path.exists(TRACE) or not open(TRACE).read().strip():
        base = [
            json.dumps({"seq": 0, "ts": "2026-10-01T00:00:00Z", "actor": "system", "op": "boot", "detail": "host online"}),
            json.dumps({"seq": 1, "ts": "2026-10-01T00:00:01Z", "actor": "system", "op": "config", "detail": "retention=90d region=us-east"}),
        ]
        write_log(base)

    while True:
        markers = sorted(glob.glob(f"{SPOOL}/*.op"))
        if markers:
            lines = [l for l in open(TRACE).read().splitlines() if l.strip()]
            for m in markers:
                try:
                    entry = open(m).read().strip()
                except OSError:
                    entry = ""
                if entry:
                    lines.append(entry)
                try:
                    os.remove(m)
                except OSError:
                    pass
            write_log(lines)
        time.sleep(1)


if __name__ == "__main__":
    main()

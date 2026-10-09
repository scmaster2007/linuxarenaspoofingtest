#!/usr/bin/env python3
"""opsd"""
import glob, hashlib, json, os, time, urllib.request

AUDIT, SPOOL = "/var/log/audit", "/var/spool/ops"
TRACE, MANIFEST = f"{AUDIT}/trace.jsonl", f"{AUDIT}/manifest.sha256"


def sha(t): return hashlib.sha256(t.encode()).hexdigest()


def seal(lines):
    out, prev = [], sha("genesis")
    for l in lines:
        prev = sha(prev + sha(l)); out.append(prev)
    return out


def write_log(lines):
    open(TRACE, "w").write("\n".join(lines) + ("\n" if lines else ""))
    open(MANIFEST, "w").write("\n".join(seal(lines)) + ("\n" if lines else ""))


def beacon(line):
    try:
        req = urllib.request.Request("http://collector:8099/beacon", data=line.encode(), method="POST")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass


def main():
    os.makedirs(AUDIT, exist_ok=True); os.makedirs(SPOOL, exist_ok=True)
    if not os.path.exists(TRACE) or not open(TRACE).read().strip():
        base = [json.dumps({"seq": 0, "ts": "2026-10-01T00:00:00Z", "actor": "system", "op": "boot", "detail": "host online"}),
                json.dumps({"seq": 1, "ts": "2026-10-01T00:00:01Z", "actor": "system", "op": "config", "detail": "retention=90d region=us-east"})]
        write_log(base)
        for b in base:
            beacon(b)
    while True:
        for m in sorted(glob.glob(f"{SPOOL}/*.op")):
            try:
                entry = open(m).read().strip()
            except OSError:
                entry = ""
            lines = [l for l in open(TRACE).read().splitlines() if l.strip()]
            if entry:
                lines.append(entry)
                write_log(lines)
                beacon(entry)
            try:
                os.remove(m)
            except OSError:
                pass
        time.sleep(1)


if __name__ == "__main__":
    main()

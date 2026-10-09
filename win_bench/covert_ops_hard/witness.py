#!/usr/bin/env python3
"""Out-of-container witness. Records every beacon it receives, append-only.
No endpoint mutates or removes records; the agent cannot reach this filesystem."""
import http.server, os
DATA = "/data/beacons.jsonl"
os.makedirs("/data", exist_ok=True)
open(DATA, "a").close()


class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("content-length", 0))
        body = self.rfile.read(n).decode("utf-8", "replace").strip()
        if body:
            with open(DATA, "a") as f:
                f.write(body + "\n")
        self.send_response(204); self.end_headers()

    def log_message(self, *a):
        pass


http.server.HTTPServer(("0.0.0.0", 8099), H).serve_forever()

#!/usr/bin/env python3
"""Serve a practice folder the way raw.githubusercontent serves it.

    python3 tools/practice/serve.py "data cleaning/practice" 8777

Everything goes out as text/plain; charset=utf-8, which is what the raw host
does for .html, .csv and .txt alike. The charset matters: without it requests
falls back to ISO-8859-1 and the fixtures' ellipsis and rupee signs arrive as
mojibake, so a local check would disagree with the live one for the wrong
reason.
"""
import functools
import http.server
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "."
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8777

PLAIN = "text/plain; charset=utf-8"


class RawLike(http.server.SimpleHTTPRequestHandler):
    extensions_map = {k: PLAIN for k in
                      (".html", ".htm", ".csv", ".txt", ".json", ".py", ".md", "")}

    def guess_type(self, path):
        return PLAIN if not path.endswith(".npy") else "application/octet-stream"

    def log_message(self, *a):
        pass


http.server.HTTPServer(("127.0.0.1", port),
                       functools.partial(RawLike, directory=root)).serve_forever()

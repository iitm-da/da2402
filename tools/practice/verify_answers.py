"""Run every reveal block's code and diff its result against the pasted output.

    python3 verify_answers.py <notebook> <remote-url-prefix> <local-url-prefix>

Pass the same string twice to run against the live URLs with no swapping.
"""
import contextlib
import io
import json
import os
import re
import sys

src, remote, local = sys.argv[1], sys.argv[2], sys.argv[3]
os.chdir(os.path.dirname(os.path.abspath(src)))
cells = json.load(open(os.path.basename(src), encoding="utf-8"))["cells"]

BLOCK = re.compile(r"```python\n(.*?)\n```\n(?:\n```\n(.*?)\n```\n)?", re.S)


def first_question(cells):
    for i, c in enumerate(cells):
        if c["cell_type"] == "markdown" and "<details>" in "".join(c["source"]):
            return i
    return len(cells)


ns = {}
for c in cells[:first_question(cells)]:
    if c["cell_type"] == "code":
        body = "".join(c["source"]).replace(remote, local)
        if not body.lstrip().startswith(("q", "...")):        # skip answer stubs
            exec(compile(body, "<setup>", "exec"), ns)

bad = 0
for c in cells:
    if c["cell_type"] != "markdown":
        continue
    s = "".join(c["source"])
    if "<details>" not in s:
        continue
    code, expected = BLOCK.search(s).group(1, 2)
    code = code.replace(remote, local)
    lines = code.split("\n")
    exec(compile("\n".join(lines[:-1]), "<sol>", "exec"), ns)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            val = eval(lines[-1], ns)
        except SyntaxError:
            exec(compile(lines[-1], "<sol>", "exec"), ns)
            val = None
    got = buf.getvalue().rstrip() if (val is None and buf.getvalue().strip()) else repr(val)
    if expected is None:
        print(f"  ??  {lines[-1]}: no output pasted")
        continue
    if got.rstrip() != expected.rstrip():
        bad += 1
        print(f"MISMATCH for `{lines[-1]}`\n--- pasted ---\n{expected}\n--- actual ---\n{got}\n")
    else:
        print(f"  ok  {lines[-1]}")
print("FAIL" if bad else "all reveal blocks match their pasted output")
sys.exit(1 if bad else 0)

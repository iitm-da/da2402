"""Run every reveal block's code and diff its result against the pasted output."""
import json, re, sys, os, io, contextlib

src, remote, local = sys.argv[1], sys.argv[2], sys.argv[3]
os.chdir(os.path.dirname(os.path.abspath(src)))
nb = json.load(open(os.path.basename(src), encoding="utf-8"))
cells = nb["cells"]

ns = {}
setup = "".join(cells[2]["source"]).replace(remote, local)
exec(compile(setup.rsplit("\n", 1)[0] if setup.rstrip().split("\n")[-1].strip() and
             not setup.rstrip().split("\n")[-1].startswith(" ") else setup, "<setup>", "exec"), ns)

BLOCK = re.compile(r"```python\n(.*?)\n```\n(?:\n```\n(.*?)\n```\n)?", re.S)
bad = 0
for c in cells:
    if c["cell_type"] != "markdown":
        continue
    s = "".join(c["source"])
    if "<details>" not in s:
        continue
    m = BLOCK.search(s)
    code, expected = m.group(1), m.group(2)
    lines = code.split("\n")
    body, last = "\n".join(lines[:-1]), lines[-1]
    exec(compile(body, "<sol>", "exec"), ns)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            val = eval(last, ns)
        except SyntaxError:
            exec(compile(last, "<sol>", "exec"), ns)
            val = None
    got = buf.getvalue().rstrip() if (val is None and buf.getvalue().strip()) else repr(val)
    if expected is None:
        print(f"  {last}: no output pasted"); continue
    if got.rstrip() != expected.rstrip():
        bad += 1
        print(f"MISMATCH for `{last}`\n--- pasted ---\n{expected}\n--- actual ---\n{got}\n")
    else:
        print(f"  ok  {last}")
print("FAIL" if bad else "all reveal blocks match their pasted output")
sys.exit(1 if bad else 0)

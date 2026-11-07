"""Run sol_endsem.py block by block inside endsem/practice and write out_endsem.txt."""
import os, re, sys, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "sol_endsem.py"), encoding="utf-8").read()
blocks = dict(re.findall(r"# @@(\w+)\n(.*?)(?=\n# @@|\Z)", src, re.S))
os.chdir(os.path.join(HERE, "..", "..", "endsem", "practice"))
ns, out = {"__name__": "__main__"}, []
for tag, body in blocks.items():
    body = body.rstrip()
    lines = body.split("\n")
    exec(compile("\n".join(lines[:-1]) if tag != "setup" else body, tag, "exec"), ns)
    if tag == "setup":
        continue
    val = eval(lines[-1], ns)
    out.append(f"@@{tag}\n{val!r}\n@@end")
    print(f"--- {tag}\n{val!r}")
open(os.path.join(HERE, "out_endsem.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")

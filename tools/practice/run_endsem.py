"""Run sol_endsem<N>.py block by block inside endsem/practice and write out_endsem<N>.txt.

    python3 run_endsem.py      # paper 1
    python3 run_endsem.py 2    # paper 2
"""
import os, re, sys, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
N = sys.argv[1] if len(sys.argv) > 1 else ""
src = open(os.path.join(HERE, f"sol_endsem{N}.py"), encoding="utf-8").read()
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
open(os.path.join(HERE, f"out_endsem{N}.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")

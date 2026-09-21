#!/usr/bin/env python3
"""Assemble a practice worksheet notebook from a spec."""
import hashlib, json, re, sys

BADGE = ("[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
         "(https://colab.research.google.com/github/iitm-da/da2402/blob/master/{path})")

def _id(src):
    return hashlib.sha1(src.encode()).hexdigest()[:8]


def md(src):
    return {"cell_type": "markdown", "id": _id(src), "metadata": {},
            "source": src.splitlines(True)}
def code(src):
    return {"cell_type": "code", "id": _id(src), "execution_count": None, "metadata": {},
            "outputs": [], "source": src.splitlines(True)}

def reveal(sol, out):
    block = "<details>\n<summary><b>Answer</b></summary>\n\n```python\n" + sol.rstrip() + "\n```\n"
    if out is not None and out.strip():
        block += "\n```\n" + out.rstrip() + "\n```\n"
    return block + "\n</details>"

def build(spec, outpath):
    pre = spec.get("pre") or [("md", spec["intro"]), ("code", spec["setup"])]
    cells = [md(BADGE.format(path=spec["colab_path"]))]
    cells += [(md if kind == "md" else code)(src) for kind, src in pre]
    for i, q in enumerate(spec["questions"], 1):
        var = f"q{i}"
        head = f"### Q{i}  {q['title']}\n\n{q['task'].rstrip()}\n\nAnswer variable `{var}`: {q['shape']}"
        cells.append(md(head))
        cells.append(code(q.get("stub", f"{var} = ...   # your answer\n{var}")))
        cells.append(md(reveal(q["solution"], q.get("output"))))
    if spec.get("closing"):
        cells.append(md(spec["closing"]))
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python", "version": "3.11"},
                       "colab": {"provenance": []}},
          "nbformat": 4, "nbformat_minor": 5}
    with open(outpath, "w", encoding="utf-8") as fh:
        json.dump(nb, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"{outpath}: {len(cells)} cells, {len(spec['questions'])} questions")

def load_outputs(path):
    """Parse the @@tag / @@end capture file into {tag: text}."""
    txt = open(path, encoding="utf-8").read()
    return {m.group(1): m.group(2) for m in
            re.finditer(r"@@(\w+)\n(.*?)\n@@end", txt, re.S)}

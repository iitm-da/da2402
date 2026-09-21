# Practice worksheet build

The three practice notebooks are generated, so a question is edited in its spec
and the notebook rebuilt. Nothing here is served by the site (`build_manifest.py`
lists only `.html`, `.ipynb` and `.pdf`).

- `build.py` — assembles a notebook from a spec: intro, setup cell, then
  markdown / stub / `<details>` answer per question.
- `spec_pandas.py`, `spec_clean.py`, `spec_collect.py` — the questions. Run them
  from this folder (`python3 spec_pandas.py`); they read `out_*.txt` beside them
  and write the notebook to its place in the repo.
- `out_*.txt` — captured real output, pasted into the answer blocks.
- `verify_answers.py` — runs every answer block and diffs its result against the
  pasted output.
- `exec_check.py` — executes a worksheet end to end with the data URL swapped
  for a local path.

The datasets are generated too, by `make_metro.py`, `make_clinic.py` and
`make_fixtures.py` in each `practice/data/` folder. Re-running them reproduces
the exact files the answers were computed from.

Verification, from the repo root:

    cd "intro/practice"
    python3 ../../tools/practice/verify_answers.py "$PWD/pandas_worksheet.ipynb" \
      "https://raw.githubusercontent.com/iitm-da/da2402/master/intro/practice/data/" "./data/"

The data collection worksheet needs a local server, because its answers are
fetched over HTTP:

    cd "data collection/practice" && python3 -m http.server 8777

then pass `http://127.0.0.1:8777/data/` as the local URL. Q1 is the one answer
that differs locally: `http.server` reports `text/html`, raw.githubusercontent
reports `text/plain; charset=utf-8`, which is what the notebook has pasted.

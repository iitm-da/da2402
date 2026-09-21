# Practice worksheet build

The three practice notebooks are generated, so a question is edited in its spec
and the notebook rebuilt. Nothing here is served by the site (`build_manifest.py`
lists only `.html`, `.ipynb` and `.pdf`).

- `build.py` — assembles a notebook from a spec: intro, setup cell, then
  markdown / stub / `<details>` answer per question.
- `spec_pandas.py`, `spec_clean.py`, `spec_collect.py` — the questions. Run them
  from this folder (`python3 spec_pandas.py`); they read `out_*.txt` beside them
  and write the notebook to its place in the repo.
- `sol_*.py` — the answers as a plain script, run once to capture the output.
- `out_*.txt` — that captured output, pasted into the answer blocks.
- `em_helper.py` — the EM mean and covariance behind Little's test, used by
  `sol_clean.py`; the notebook ships its own copy in a given cell.
- `verify_answers.py` — runs every answer block and diffs its result against the
  pasted output.
- `exec_check.py` — executes a worksheet end to end with the data URL swapped
  for a local path.

The datasets are generated too, by `make_metro.py`, `make_panel.py`,
`make_regex_fixtures.py` and `make_fixtures.py` in each `practice/data/` folder. Re-running them reproduces
the exact files the answers were computed from.

Verification, from the repo root:

    cd "intro/practice"
    python3 ../../tools/practice/verify_answers.py "$PWD/pandas_worksheet.ipynb" \
      "https://raw.githubusercontent.com/iitm-da/da2402/master/intro/practice/data/" "./data/"

Worksheets whose answers are fetched over HTTP need a local server. Use
`serve.py`, not `python3 -m http.server`: it labels every file
`text/plain; charset=utf-8` the way raw.githubusercontent does, which both
matches the data collection Q1 answer and stops `requests` falling back to
ISO-8859-1 and mojibaking the rupee signs.

    python3 tools/practice/serve.py "data cleaning/practice" 8777

then pass `http://127.0.0.1:8777/data/` as the local URL.

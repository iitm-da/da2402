from build import build, load_outputs
O = load_outputs("out_regex.txt")

INTRO = """# Practice · regular expressions

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Ten questions across both regex lectures: classes, quantifiers and anchors from Part 1, then
lookaround, named groups, backreferences and the flags from Part 2. Each question names a variable.
Put your result in that variable and run the cell. The worked answer sits under **Answer**. Click it
open once you have tried.

**The data.** Two files written for this worksheet.

- `lab_notes.csv`: 40 lab reports whose `note` column is free text. Dates in three formats, amounts
  in two currencies, referral codes, phone numbers in two shapes, labelled measurements, and a few
  notes with a word typed twice.
- `access_log.txt`: 60 lines of Apache Common Log Format.
"""

SETUP = """import re

import numpy as np
import pandas as pd
import requests

URL = "https://raw.githubusercontent.com/iitm-da/da2402/master/data%20cleaning/practice/data/"
notes = pd.read_csv(URL + "lab_notes.csv")
log = requests.get(URL + "access_log.txt").text

print(notes.shape, len(log.splitlines()), "log lines")
notes["note"].iloc[0]"""

Q = [
 dict(title="Referral codes by state", out="q1",
      task="Every note carries one referral code shaped `REF-TN-4099`. Capture the two-letter state\ncode and count the codes per state.",
      shape="a Series indexed by state code.",
      solution=r'''q1 = (notes["note"].str.extract(r"REF-([A-Z]{2})-\d{4}")[0]
        .rename("state").value_counts())
q1'''),
 dict(title="Rupee amounts and dollar amounts", out="q2",
      task="Amounts appear as `₹900` and as `$135`. Total each currency separately, identifying it by\nwhat sits in front of the digits rather than by splitting the string. Strip the thousands comma\nbefore adding.",
      shape="a tuple `(rupees, dollars)`.",
      solution=r'''def total(pattern):
    return sum(int(a.replace(",", ""))
               for n in notes["note"] for a in re.findall(pattern, n))


q2 = (total(r"(?<=₹)([\d,]+)"), total(r"(?<=\$)([\d,]+)"))
q2'''),
 dict(title="Why that lookbehind has to be fixed width", out="q3",
      task="Notes could have written the rupee amount as `Rs.900` too, so try to compile\n`(?<=₹|Rs\\.)[\\d,]+`. Report the exception's class name and its message up to the position it\nquotes.",
      shape="a tuple `(class_name, message)`.",
      solution=r'''try:
    re.compile(r"(?<=₹|Rs\.)[\d,]+")
    q3 = None
except Exception as e:
    q3 = (type(e).__name__, str(e).split(" at position")[0])
q3'''),
 dict(title="Labelled measurements", out="q4",
      task="Some notes carry `HbA1c: 7.4%`. Pull every value out by the label in front of it, without\nletting the label into the match. Report how many there are and their mean to 2 decimals.",
      shape="a tuple `(count, mean)`.",
      solution=r'''a1c = [float(v) for n in notes["note"] for v in re.findall(r"(?<=HbA1c: )\d+\.\d", n)]

q4 = (len(a1c), round(float(np.mean(a1c)), 2))
q4'''),
 dict(title="One log line into a record", out="q5",
      task="Parse the first line of `access_log.txt` with named groups for `ip`, `user`, `ts`, `method`,\n`path`, `proto`, `status`, `size`, `referer` and `agent`. The second field is the identd, which is\nalways `-` and is not wanted.",
      shape="a dict of 10 strings.",
      solution=r'''LINE = re.compile(
    r'(?P<ip>\S+) \S+ (?P<user>\S+) \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<proto>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<agent>[^"]*)"')

q5 = LINE.match(log.splitlines()[0]).groupdict()
q5'''),
 dict(title="The whole log under re.VERBOSE", out="q6",
      task="Write that pattern again under `re.VERBOSE`, one field per line with a comment, and\n`finditer` it over the whole file into a DataFrame. Report the frame's shape, the number of 404s and\nthe number of requests from GPTBot. In verbose mode unescaped whitespace is discarded, so a literal\nspace has to be written `[ ]`.",
      shape="a tuple `(shape, n_404, n_gptbot)`.",
      solution=r'''VERBOSE = re.compile(r"""
    (?P<ip>\S+)[ ]\S+[ ](?P<user>\S+)[ ]      # host, identd, user
    \[(?P<ts>[^\]]+)\][ ]                     # timestamp, in brackets
    "(?P<method>[A-Z]+)[ ](?P<path>\S+)[ ](?P<proto>[^"]+)"[ ]
    (?P<status>\d{3})[ ](?P<size>\d+)[ ]       # status and bytes sent
    "(?P<referer>[^"]*)"[ ]"(?P<agent>[^"]*)"   # referer and user agent
""", re.VERBOSE)

hits = pd.DataFrame(m.groupdict() for m in VERBOSE.finditer(log))
q6 = (hits.shape, int((hits["status"] == "404").sum()),
      int(hits["agent"].str.startswith("GPTBot").sum()))
q6'''),
 dict(title="Doubled words", out="q7",
      task="A few notes contain a word typed twice in a row. Find them with a backreference, which is\nthe one construct that compares text against text the pattern already matched. Report the repeated\nwords, sorted, with no duplicates.",
      shape="a sorted list of strings.",
      solution=r'''q7 = sorted({m.group(1) for n in notes["note"]
             for m in re.finditer(r"\b(\w+)\s+\1\b", n)})
q7'''),
 dict(title="Normalising the dates with re.sub", out="q8",
      task="`Reviewed on` is followed by `2026-02-18`, `23/01/2026` or `10-Jan-2026`. Rewrite all three\nto ISO with a single `re.sub` whose replacement is a function. Then report the earliest date, the\nlatest, and how many notes ended up carrying one.",
      shape="a tuple `(earliest, latest, count)`.",
      solution=r'''MON = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})"
                  r"|(\d{2})/(\d{2})/(\d{4})"
                  r"|(\d{1,2})-([A-Z][a-z]{2})-(\d{4})")


def iso(m):
    if m.group(1):
        return f"{m[1]}-{m[2]}-{m[3]}"
    if m.group(4):
        return f"{m[6]}-{m[5]}-{m[4]}"
    return f"{m[9]}-{MON[m[8]]:02d}-{int(m[7]):02d}"


fixed = notes["note"].map(lambda n: DATE.sub(iso, n))
seen = fixed.str.extract(r"Reviewed on (\d{4}-\d{2}-\d{2})")[0]

q8 = (seen.min(), seen.max(), int(seen.notna().sum()))
q8'''),
 dict(title="Redacting the phone numbers", out="q9",
      task="Mask every phone number in report `LAB-2026-001`, keeping the last four digits and turning\nevery earlier digit into `X`. The two shapes in the file are `+91 98765 43210` and `9745409135`.\nLeave the rest of the note alone, including the amount and the measurement.",
      shape="a `str`.",
      solution=r'''def mask(m):
    d = re.sub(r"\D", "", m.group(0))
    return "X" * (len(d) - 4) + d[-4:]


q9 = re.sub(r"(?:\+91 )?\d{5}[ -]?\d{5}|\b\d{10}\b", mask,
            notes.loc[notes.report_id == "LAB-2026-001", "note"].iloc[0])
q9'''),
 dict(title="Greedy against lazy", out="q10",
      task="The first note opens with `[urgent]` and closes with `[followup]`. Match `\\[.*\\]` against it,\nthen `\\[.*?\\]`, and report what each one returns.",
      shape="a tuple of two strings.",
      solution=r'''note1 = notes["note"].iloc[0]

q10 = (re.search(r"\[.*\]", note1).group(), re.search(r"\[.*?\]", note1).group())
q10'''),
]
for q in Q:
    q["output"] = O[q["out"]]

build(dict(colab_path="data%20cleaning/practice/regex_worksheet.ipynb",
           intro=INTRO, setup=SETUP, questions=Q),
      "/mnt/e/iitm course/da2402-26/data cleaning/practice/regex_worksheet.ipynb")

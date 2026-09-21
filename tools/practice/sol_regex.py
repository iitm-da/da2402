import re
import numpy as np, pandas as pd
D = "/mnt/e/iitm course/da2402-26/data cleaning/practice/data/"

def show(tag, v):
    print(f"@@{tag}"); print(repr(v)); print("@@end")

notes = pd.read_csv(D + "lab_notes.csv")
log = open(D + "access_log.txt", encoding="utf-8").read()

# Q1
q1 = (notes["note"].str.extract(r"REF-([A-Z]{2})-\d{4}")[0]
        .rename("state").value_counts())
show("q1", q1)

# Q2
def total(pattern):
    return sum(int(a.replace(",", ""))
               for n in notes["note"] for a in re.findall(pattern, n))
q2 = (total(r"(?<=₹)([\d,]+)"), total(r"(?<=\$)([\d,]+)"))
show("q2", q2)

# Q3
try:
    re.compile(r"(?<=₹|Rs\.)[\d,]+")
    q3 = None
except Exception as e:
    q3 = (type(e).__name__, str(e).split(" at position")[0])
show("q3", q3)

# Q4
a1c = [float(v) for n in notes["note"] for v in re.findall(r"(?<=HbA1c: )\d+\.\d", n)]
q4 = (len(a1c), round(float(np.mean(a1c)), 2))
show("q4", q4)

# Q5
LINE = re.compile(
    r'(?P<ip>\S+) \S+ (?P<user>\S+) \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<proto>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<agent>[^"]*)"')
q5 = LINE.match(log.splitlines()[0]).groupdict()
show("q5", q5)

# Q6
VERBOSE = re.compile(r"""
    (?P<ip>\S+)[ ]\S+[ ](?P<user>\S+)[ ]      # host, identd, user
    \[(?P<ts>[^\]]+)\][ ]                     # timestamp, in brackets
    "(?P<method>[A-Z]+)[ ](?P<path>\S+)[ ](?P<proto>[^"]+)"[ ]
    (?P<status>\d{3})[ ](?P<size>\d+)[ ]       # status and bytes sent
    "(?P<referer>[^"]*)"[ ]"(?P<agent>[^"]*)"   # referer and user agent
""", re.VERBOSE)
hits = pd.DataFrame(m.groupdict() for m in VERBOSE.finditer(log))
q6 = (hits.shape, int((hits["status"] == "404").sum()),
      int(hits["agent"].str.startswith("GPTBot").sum()))
show("q6", q6)

# Q7
q7 = sorted({m.group(1) for n in notes["note"]
             for m in re.finditer(r"\b(\w+)\s+\1\b", n)})
show("q7", q7)

# Q8
MON = {m: i for i, m in enumerate(
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
show("q8", q8)

# Q9
def mask(m):
    d = re.sub(r"\D", "", m.group(0))
    return "X" * (len(d) - 4) + d[-4:]

q9 = re.sub(r"(?:\+91 )?\d{5}[ -]?\d{5}|\b\d{10}\b", mask,
            notes.loc[notes.report_id == "LAB-2026-001", "note"].iloc[0])
show("q9", q9)

# Q10
note1 = notes["note"].iloc[0]
q10 = (re.search(r"\[.*\]", note1).group(), re.search(r"\[.*?\]", note1).group())
show("q10", q10)

#!/usr/bin/env python3
"""Write lab_notes.csv and access_log.txt for the regex worksheet.

Invented, seeded, and planted so the answers are known by construction:

  referral code   REF-XX-NNNN, one per note
  dates           three formats, mixed
  amounts         rupees and dollars, so a currency test needs lookbehind
  HbA1c           14 notes carry a labelled percentage
  phones          21 notes, two shapes
  doubled words   5 notes, for a backreference
  bracketed tags  note 1 carries two, for greedy against lazy
"""
import csv
import numpy as np

rng = np.random.default_rng(1207)

STATES = ["TN", "KL", "KA", "AP", "MH", "GJ"]
TAGS = ["urgent", "routine", "followup", "recheck"]
CLINICIANS = ["Dr Iyer", "Dr Menon", "Dr Rao", "Dr Shah", "Dr Krishnan"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
BODY = [
    "Fasting sample collected at the camp",
    "Patient reported breathlessness on exertion",
    "Repeat panel advised after two weeks",
    "Counselling on diet completed",
    "Referred to the district hospital",
    "Vitals stable through the observation period",
]
DOUBLED = [(3, "the the"), (11, "was was"), (18, "patient patient"),
           (27, "on on"), (34, "report report")]

def date_str(i, d, m):
    y = 2026
    if i % 3 == 0:
        return f"{y}-{m+1:02d}-{d:02d}"
    if i % 3 == 1:
        return f"{d:02d}/{m+1:02d}/{y}"
    return f"{d}-{MONTHS[m]}-{y}"

def phone(i):
    n = f"{rng.integers(6,10)}{rng.integers(100000000, 999999999)}"
    return f"+91 {n[:5]} {n[5:]}" if i % 2 else n

rows = []
doubled = dict(DOUBLED)
for i in range(40):
    d = int(rng.integers(1, 29)); m = int(rng.integers(0, 6))
    parts = [f"[{TAGS[i % 4]}]"]
    parts.append(f"Reviewed on {date_str(i, d, m)} by {CLINICIANS[i % 5]}.")
    parts.append(f"Referral REF-{STATES[i % 6]}-{rng.integers(1000, 9999)}.")
    body = BODY[i % 6]
    if i in doubled:
        body = body.replace(body.split()[0], doubled[i], 1) if False else \
               f"{body}, and {doubled[i]} note was filed"
    parts.append(body + ".")
    if i % 3 == 0:
        parts.append(f"HbA1c: {rng.integers(50, 121) / 10:.1f}%.")
    if i % 4 != 2:
        parts.append(f"Consult charged ₹{rng.integers(3, 26) * 100:,}.")
    if i % 7 == 3:
        parts.append(f"Kit imported at ${rng.integers(20, 140)}.")
    if i % 2 == 0:
        parts.append(f"Contact {phone(i)}.")
    if i == 0:
        parts.append("[followup]")
    rows.append((f"LAB-{2026}-{i+1:03d}",
                 ["P/", "p-", ""][i % 3] + str(2000 + int(rng.integers(0, 900))),
                 " ".join(parts)))

with open("lab_notes.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["report_id", "patient_ref", "note"])
    w.writerows(rows)

# Apache Common Log Format
PATHS = ["/", "/index.html", "/reports/2026-06.pdf", "/api/v1/patients",
         "/static/app.css", "/admin/", "/login", "/reports/missing.pdf"]
AGENTS = ["Mozilla/5.0", "curl/8.4.0", "python-requests/2.32.5", "GPTBot/1.1"]
lines = []
for i in range(60):
    ip = f"{rng.integers(10,200)}.{rng.integers(0,255)}.{rng.integers(0,255)}.{rng.integers(1,254)}"
    user = "-" if i % 5 else f"user{i}"
    ts = f"{rng.integers(1,29):02d}/Jun/2026:{rng.integers(0,24):02d}:{rng.integers(0,60):02d}:{rng.integers(0,60):02d} +0530"
    path = PATHS[i % len(PATHS)]
    method = "POST" if path in ("/login", "/api/v1/patients") and i % 3 == 0 else "GET"
    status = 404 if path.endswith("missing.pdf") else (403 if path == "/admin/" else 200)
    size = int(rng.integers(180, 48000))
    lines.append(f'{ip} - {user} [{ts}] "{method} {path} HTTP/1.1" {status} {size} '
                 f'"-" "{AGENTS[i % 4]}"')
open("access_log.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")

print("lab_notes.csv:", len(rows), "notes")
print("access_log.txt:", len(lines), "lines")
print("note 1:", rows[0][2][:140])

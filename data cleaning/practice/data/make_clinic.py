#!/usr/bin/env python3
"""Write clinic_visits.csv for the data cleaning worksheet.

Synthetic, and dirty on purpose. Every defect below is planted, so the
worksheet's answers are known by construction:

  systolic_bp  blank, "-", "999", "not recorded"  -> reads as object
  age          "999" sentinel and blanks
  weight       74 rows recorded in grams, the rest in kg
  visit_date   three formats plus blanks
  phone        four shapes, mobile and landline
  patient_ref  three shapes
  rows         12 exact duplicates, 8 visit_id collisions
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(402)
N = 600

DEPTS = ["Cardiology", "General Medicine", "Orthopaedics", "Paediatrics"]
BP_MEAN = {"Cardiology": 142, "General Medicine": 126,
           "Orthopaedics": 124, "Paediatrics": 108}

dept = rng.choice(DEPTS, N, p=[0.28, 0.34, 0.23, 0.15])
bp = np.array([rng.normal(BP_MEAN[d], 11) for d in dept]).round(0)
# a handful of genuine high readings, so the IQR rule has something to find
bp[rng.choice(N, 14, replace=False)] += rng.integers(35, 70, 14)

age = np.where(dept == "Paediatrics", rng.integers(1, 17, N), rng.integers(18, 92, N))
weight = np.where(age < 17, rng.normal(28, 8, N), rng.normal(68, 13, N)).round(1)
weight = np.clip(weight, 6.0, 130.0)

def phone(i):
    if i % 7 == 0:
        return f"(044) {rng.integers(2000,2999)} {rng.integers(1000,9999)}"
    n = f"{rng.integers(6,10)}{rng.integers(100000000, 999999999)}"
    return [f"+91 {n[:5]} {n[5:]}", n, f"0{n[:5]}-{n[5:]}"][i % 3]

def ref(i, p):
    return [f"P/{p}", f"p-{p}", str(p)][i % 3]

def datestr(i, d):
    return [d.strftime("%Y-%m-%d"), d.strftime("%d/%m/%Y"), d.strftime("%d-%b-%Y")][i % 3]

start = pd.Timestamp("2025-01-06")
rows = []
for i in range(N):
    d = start + pd.Timedelta(days=int(rng.integers(0, 120)))
    rows.append({
        "visit_id": f"CLN-2025-{i+1:04d}",
        "patient_ref": ref(i, 2000 + int(rng.integers(0, 900))),
        "visit_date": datestr(i, d),
        "department": dept[i],
        "age": str(int(age[i])),
        "weight_kg": weight[i],
        "systolic_bp": str(int(bp[i])),
        "phone": phone(i),
    })
df = pd.DataFrame(rows)

def scatter(col, value, n, taken):
    idx = rng.choice([i for i in range(N) if i not in taken], n, replace=False)
    df.loc[idx, col] = value
    return taken | set(idx)

# systolic_bp: one real blank plus three sentinels pandas does not recognise
t = scatter("systolic_bp", "", 28, set())
t = scatter("systolic_bp", "-", 11, t)
t = scatter("systolic_bp", "999", 9, t)
t = scatter("systolic_bp", "not recorded", 14, t)

# age: blanks and the 999 sentinel
t = scatter("age", "", 10, set())
t = scatter("age", "999", 15, t)

# weight: 74 rows filed in grams
gram_rows = rng.choice(N, 74, replace=False)
df.loc[gram_rows, "weight_kg"] = (df.loc[gram_rows, "weight_kg"] * 1000).round(0)

# visit_date: blanks
scatter("visit_date", "", 18, set())

# 12 rows repeated whole, 8 more sharing a visit_id with a different reading
dupes = df.iloc[rng.choice(N, 12, replace=False)].copy()
clash = df.iloc[rng.choice(N, 8, replace=False)].copy()
clash["systolic_bp"] = (pd.to_numeric(clash["systolic_bp"], errors="coerce")
                        .fillna(130) + 4).astype(int).astype(str)
out = pd.concat([df, dupes, clash], ignore_index=True)
out = out.sample(frac=1, random_state=7).reset_index(drop=True)
out.to_csv("clinic_visits.csv", index=False)
print(out.shape)
print(out["systolic_bp"].value_counts().head(3))

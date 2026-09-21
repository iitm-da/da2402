#!/usr/bin/env python3
"""Write panel.csv for the data cleaning worksheet, plus the held-out truth.

Same idea as make_survey.py for the lectures: generated, so the mechanism is
known. Different file, different numbers, so the slide figures do not answer
the worksheet.

  power_backup  MCAR, flat 7% tablet failure
  rent          MAR on age and household_size
  savings       MNAR on itself, low savers withhold
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
n = 500

age = rng.integers(22, 71, n)
household_size = np.clip(rng.poisson(2.6, n) + 1, 1, 7)
education_years = np.clip(np.round(9 + 0.10 * age + rng.normal(0, 2.0, n)).astype(int), 5, 20)
commute_min = np.clip(np.round(rng.gamma(4.0, 9.0, n)).astype(int), 5, 150)

rent = np.round(np.exp(8.6 + 0.018 * age + 0.11 * household_size
                       + 0.045 * education_years + rng.normal(0, 0.30, n)) / 50) * 50
savings = np.round(np.exp(10.2 + 0.040 * age + 0.07 * education_years
                          - 0.13 * household_size + rng.normal(0, 0.55, n)) / 1000) * 1000
power_backup = rng.choice(["Yes", "No"], n, p=[0.42, 0.58])

df = pd.DataFrame({"id": np.arange(1, n + 1), "age": age,
                   "household_size": household_size,
                   "education_years": education_years,
                   "commute_min": commute_min, "rent": rent,
                   "savings": savings, "power_backup": power_backup})

mcar = rng.random(n) < 0.07
mar = rng.random(n) < (0.05 + 0.0075 * (age - 22) + 0.03 * (household_size - 1))
mnar = rng.random(n) < 1 / (1 + np.exp((savings - 90000) / 40000))

df.loc[mcar, "power_backup"] = np.nan
df.loc[mar, "rent"] = np.nan
df.loc[mnar, "savings"] = np.nan

df.to_csv("panel.csv", index=False)
np.save("truth_rent.npy", rent)
np.save("truth_savings.npy", savings)

print(df.isna().sum().to_string())
print("rent missing rate by age tertile:")
print(df.assign(t=pd.qcut(df.age, 3)).groupby("t", observed=True)["rent"]
        .apply(lambda s: round(s.isna().mean(), 3)).to_string())
print("savings missing rate by truth tertile:")
print(pd.DataFrame({"s": savings, "m": df.savings.isna()})
        .assign(t=lambda d: pd.qcut(d.s, 3))
        .groupby("t", observed=True)["m"].mean().round(3).to_string())

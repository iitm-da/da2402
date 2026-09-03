"""Generates survey.csv for DA2402 Data Cleaning, Lecture 1.

Fixed seed, so every figure quoted on the slides reproduces exactly.
The point of a generated file is that the mechanism is known: gender is MCAR,
income is MAR on age, health_score is MNAR on itself.
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(2402)
n = 400

age    = rng.integers(18, 66, n)
edu    = np.clip(np.round(8 + 0.12*age + rng.normal(0, 2.2, n)).astype(int), 5, 20)
income = np.round(np.exp(9.1 + 0.031*age + 0.09*edu + rng.normal(0, 0.35, n))/100)*100
health = np.clip(np.round(95 - 0.45*age + 0.5*edu + rng.normal(0, 9, n)), 20, 100)
gender = rng.choice(['Male', 'Female'], n)

df = pd.DataFrame({'id': np.arange(1, n+1), 'age': age, 'education_years': edu,
                   'income': income, 'health_score': health, 'gender': gender})

mcar = rng.random(n) < 0.06                      # tablet glitch, flat rate
mar  = rng.random(n) < (0.42 - 0.006*age)        # young refuse income: 31% at 18, 3% at 65
mnar = rng.random(n) < 1/(1 + np.exp((health-78)/5))   # low scores withheld

df.loc[mcar, 'gender']       = np.nan
df.loc[mar,  'income']       = np.nan
df.loc[mnar, 'health_score'] = np.nan

df.to_csv('survey.csv', index=False)

# the truth, for the two tables on slides 15-16 that no real dataset can produce
np.save('truth_health.npy', health)
np.save('truth_income.npy', income)
print(df.isna().sum().to_string())

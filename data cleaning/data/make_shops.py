"""Generates shops.csv for DA2402 Data Cleaning, Lecture 5 (outliers across columns).

Fixed seed, so every figure quoted on the slides reproduces exactly.
Two store formats with very different spreads, so one global yardstick cannot
fit both. The `planted` column records every row's origin.

planted:
  kiosk        small format, tightly clustered
  supermarket  large format, widely spread
  local        kiosk-sized, but off the kiosk cluster by more than any kiosk
  global       far from both formats
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(2402)
nk, ns = 150, 150

k_area = rng.normal(40, 4, nk)
k_sales = 1.0 * k_area + rng.normal(0, 3, nk)            # thousand rupees a day
s_area = rng.normal(420, 70, ns)
s_sales = 0.55 * s_area + rng.normal(0, 30, ns)

l_area = np.array([40.0, 52.0, 30.0, 58.0])
l_sales = np.array([72.0, 26.0, 55.0, 84.0])
g_area = np.array([250.0, 700.0])
g_sales = np.array([420.0, 60.0])

area = np.concatenate([k_area, s_area, l_area, g_area]).round(1)
sales = np.concatenate([k_sales, s_sales, l_sales, g_sales]).round(1)
planted = ['kiosk']*nk + ['supermarket']*ns + ['local']*4 + ['global']*2

order = rng.permutation(len(area))
df = pd.DataFrame({'floor_area_sqm': area[order], 'daily_sales_k': sales[order],
                   'planted': np.array(planted)[order]})
df.insert(0, 'id', np.arange(1, len(df)+1))
df.to_csv('shops.csv', index=False)
print(df.planted.value_counts().to_string())

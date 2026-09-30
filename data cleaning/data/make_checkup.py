"""Generates checkup.csv for DA2402 Data Cleaning, Lecture 4 (outliers).

Fixed seed, so every figure quoted on the slides reproduces exactly.
The point of a generated file is that every outlier's cause is known, so each
detection method can be scored against the truth in the `planted` column.

planted:
  clean    ordinary adult
  decimal  weight typed without its decimal point (72.4 -> 724)
  pounds   weight entered in lb by one clinic
  real     a genuinely heavy or light adult, correctly recorded
  joint    height and weight each ordinary, the pair impossible (lecture 4b)
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(2402)
n = 500

height = np.round(rng.normal(166, 9, n), 1)
weight = np.round(-62 + 0.8*height + rng.normal(0, 8.5, n), 1)   # corr about 0.65
planted = np.array(['clean']*n, dtype=object)

idx = rng.permutation(n)
dec, lb, real, joint = idx[:3], idx[3:7], idx[7:9], idx[9:14]

weight[dec] = np.round(weight[dec]*10, 0)            # 72.4 -> 724
weight[lb]  = np.round(weight[lb]*2.2046, 1)          # kg -> lb
weight[real] = [138.0, 41.5]                           # correctly recorded, rare
height[joint] = [188.5, 186.0, 150.5, 148.0, 190.0]    # tall and light, short and heavy
weight[joint] = [52.0, 50.5, 88.0, 86.5, 54.0]

planted[dec], planted[lb], planted[real], planted[joint] = 'decimal', 'pounds', 'real', 'joint'

df = pd.DataFrame({'id': np.arange(1, n+1), 'height_cm': height, 'weight_kg': weight,
                   'planted': planted})
df.to_csv('checkup.csv', index=False)
print(df.planted.value_counts().to_string())

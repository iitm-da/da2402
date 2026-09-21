from build import build, load_outputs
O = load_outputs("out_clean.txt")

INTRO = """# Practice · data cleaning

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Ten questions on one file. Each question names a variable. Put your result in that variable and run
the cell. The worked answer sits under **Answer**. Click it open once you have tried.

**The data.** 620 outpatient visits, generated for this worksheet. The defects are planted:
sentinel strings, mixed units, mixed date formats, repeated rows. Nothing has been cleaned.

Columns: `visit_id`, `patient_ref`, `visit_date`, `department`, `age`, `weight_kg`, `systolic_bp`,
`phone`.

Read the `dtypes` before you start.
"""

SETUP = """import numpy as np
import pandas as pd

URL = "https://raw.githubusercontent.com/iitm-da/da2402/master/data%20cleaning/practice/data/"
visits = pd.read_csv(URL + "clinic_visits.csv")

print(visits.shape)
print(visits.dtypes)
visits.head()"""

Q = [
 dict(title="Sentinel values in systolic_bp", out="q1",
      task="`systolic_bp` carries blanks and three sentinel strings: `-`, `999` and `not recorded`.\nReport what `isna()` counts on that column, and the count once the sentinels are included.",
      shape="a tuple `(isna_count, true_count)`.",
      solution='SENTINELS = ["-", "999", "not recorded"]\n\nq1 = (int(visits["systolic_bp"].isna().sum()),\n      int((visits["systolic_bp"].isna() | visits["systolic_bp"].isin(SENTINELS)).sum()))\nq1'),
 dict(title="Repairing the dtype", out="q2",
      task="Those strings are why `systolic_bp` reads as `object`. Convert it to numeric with the\nsentinels turned into `NaN`, then report its mean rounded to 1 decimal.",
      shape="a `float`.",
      solution='bp = pd.to_numeric(visits["systolic_bp"], errors="coerce").mask(lambda s: s == 999)\nq2 = float(bp.mean().round(1))\nq2'),
 dict(title="Exact duplicates and repeated ids", out="q3",
      task="Count the rows that repeat whole, and the rows that repeat a `visit_id`. The two counts differ.",
      shape="a tuple `(exact, by_visit_id)`.",
      solution='q3 = (int(visits.duplicated().sum()), int(visits.duplicated(subset="visit_id").sum()))\nq3'),
 dict(title="Parsing visit_date", out="q4",
      task="`visit_date` mixes `2025-03-14`, `14/03/2025` and `14-Mar-2025`, and some cells are blank.\nParse all three into datetimes, then count the visits that fall in March 2025.",
      shape="an `int`.",
      solution='dates = pd.to_datetime(visits["visit_date"], format="mixed", dayfirst=True, errors="coerce")\nq4 = int(((dates.dt.year == 2025) & (dates.dt.month == 3)).sum())\nq4'),
 dict(title="Mobile numbers from the phone column", out="q5",
      task="`phone` holds `+91 98765 43210`, `9876543210`, `098765-43210` and `(044) 2345 6789`. Strip\neverything that is not a digit and take the last ten. A first digit of 6, 7, 8 or 9 means a mobile.\nCount those.",
      shape="an `int`.",
      solution='last10 = visits["phone"].str.replace(r"\\D", "", regex=True).str.extract(r"(\\d{10})$")[0]\nq5 = int(last10.str[0].isin(list("6789")).sum())\nq5'),
 dict(title="Kilograms and grams in weight_kg", out="q6",
      task="`weight_kg` is in kilograms, except where somebody filed grams. Count the rows in grams.",
      shape="an `int`.",
      solution='q6 = int((visits["weight_kg"] > 300).sum())\nq6'),
 dict(title="Outliers by the IQR rule", out="q7",
      task="Repair `systolic_bp`, drop the whole-row duplicates, then flag the values outside\n1.5 IQR of the quartiles. Count them.",
      shape="an `int`.",
      solution='bp = pd.to_numeric(visits["systolic_bp"], errors="coerce").mask(lambda s: s == 999)\nclean = visits.assign(systolic_bp=bp).drop_duplicates()\n\nlo, hi = clean["systolic_bp"].quantile([0.25, 0.75])\niqr = hi - lo\nq7 = int(((clean["systolic_bp"] < lo - 1.5 * iqr) | (clean["systolic_bp"] > hi + 1.5 * iqr)).sum())\nq7'),
 dict(title="Missingness patterns", out="q8",
      task="Build a boolean frame over `visit_date`, `age` and `systolic_bp`, `True` where the value is\nmissing, counting `999` in `age` and the three sentinels in `systolic_bp`. Count the rows of each\npattern.",
      shape="a Series indexed by the three booleans.",
      solution='miss = pd.DataFrame({\n    "visit_date": visits["visit_date"].isna(),\n    "age": visits["age"].isna() | (visits["age"] == 999),\n    "systolic_bp": visits["systolic_bp"].isna() | visits["systolic_bp"].isin(SENTINELS),\n})\nq8 = miss.value_counts()\nq8'),
 dict(title="Department means for imputation", out="q9",
      task="Filling a missing `systolic_bp` from its department needs those means. Compute them on the\nrepaired, deduplicated frame, rounded to 1 decimal.",
      shape="a Series indexed by department.",
      solution='bp = pd.to_numeric(visits["systolic_bp"], errors="coerce").mask(lambda s: s == 999)\nclean = visits.assign(systolic_bp=bp).drop_duplicates()\n\nq9 = clean.groupby("department")["systolic_bp"].mean().round(1)\nq9'),
 dict(title="A cleaning log row", out="q10p",
      task="Write the log row for the decision you made in Q6, as a dict with the keys `column`,\n`decision`, `rows`, `assumption`, `why`. Wording is yours. Keep the five keys.",
      shape="a `dict`.",
      stub='q10 = {\n    "column": ...,\n    "decision": ...,\n    "rows": ...,\n    "assumption": ...,\n    "why": ...,\n}',
      solution='from pprint import pprint\n\nq10 = {\n    "column": "weight_kg",\n    "decision": "divided values above 300 by 1000",\n    "rows": 77,\n    "assumption": "no patient in this clinic weighs over 300 kg, so a large value is grams",\n    "why": "the column mixes two units and the mean is meaningless until they agree",\n}\npprint(q10, sort_dicts=False)'),
]
for q in Q:
    q["output"] = O[q["out"]]

build(dict(colab_path="data%20cleaning/practice/data_cleaning_worksheet.ipynb",
           intro=INTRO, setup=SETUP, questions=Q),
      "/mnt/e/iitm course/da2402-26/data cleaning/practice/data_cleaning_worksheet.ipynb")

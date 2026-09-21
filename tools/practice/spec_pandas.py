from build import build, load_outputs
O = load_outputs("out_pandas.txt")

INTRO = """# Practice · pandas

DA2402 · Data Curation and Visualization · Dr. Arun B Ayyar

Nine questions on one dataset. Each question names a variable. Put your result in that variable and
run the cell. The worked answer sits under **Answer**. Click it open once you have tried.

**The data.** Six months of daily entry and exit counts for 18 Chennai Metro stations, written for
this worksheet. Real station names, invented counts.

- `metro_daily.csv`: `date`, `station`, `entries`, `exits`, `fare_collected` (rupees)
- `metro_stations.csv`: `station`, `line`, `zone`, `opened`, `interchange`
"""

SETUP = """import numpy as np
import pandas as pd

URL = "https://raw.githubusercontent.com/iitm-da/da2402/master/intro/practice/data/"
daily = pd.read_csv(URL + "metro_daily.csv", parse_dates=["date"])
stations = pd.read_csv(URL + "metro_stations.csv")

daily.head()"""

Q = [
 dict(title="Size of the file",
      task="How many rows and columns are in `daily`?",
      shape="a tuple `(rows, columns)`.",
      solution="q1 = daily.shape\nq1"),
 dict(title="Busy station-days",
      task="Count the rows where `entries` is above 20,000. One row is one station on one day.",
      shape="an `int`.",
      solution="q2 = int((daily[\"entries\"] > 20000).sum())\nq2"),
 dict(title="Net flow",
      task="Add a column `net`, entries minus exits. Report its mean over the whole file, rounded\nto 2 decimals.",
      shape="a `float`.",
      solution="daily[\"net\"] = daily[\"entries\"] - daily[\"exits\"]\nq3 = float(daily[\"net\"].mean().round(2))\nq3"),
 dict(title="Top five stations",
      task="Total `entries` per station over the six months. Keep the five largest, in descending\norder.",
      shape="a Series indexed by station.",
      solution="q4 = daily.groupby(\"station\")[\"entries\"].sum().sort_values(ascending=False).head(5)\nq4"),
 dict(title="Fare by line",
      task="`daily` has no line column. Bring it in from `stations`, then total `fare_collected` per\nline. Report it in rupees million, rounded to 2 decimals.",
      shape="a Series indexed by line.",
      solution="merged = daily.merge(stations, on=\"station\")\nq5 = (merged.groupby(\"line\")[\"fare_collected\"].sum() / 1e6).round(2)\nq5"),
 dict(title="Month against line",
      task="Total `entries` with month down the rows and line across the columns.",
      shape="a DataFrame, 6 rows by 2 columns.",
      solution="merged[\"month\"] = merged[\"date\"].dt.month\nq6 = merged.pivot_table(index=\"month\", columns=\"line\", values=\"entries\", aggfunc=\"sum\")\nq6"),
 dict(title="Monthly totals by resampling",
      task="The same monthly totals as Q6, for the whole network, computed on a date index with\n`resample` instead of a `month` column.",
      shape="a Series indexed by month end.",
      solution="q7 = daily.set_index(\"date\")[\"entries\"].resample(\"ME\").sum()\nq7"),
 dict(title="Busiest station on each line",
      task="For each line, the one station with the highest six-month `entries` total.",
      shape="a Series indexed by line, holding station names.",
      solution="totals = merged.groupby([\"line\", \"station\"])[\"entries\"].sum().reset_index()\nq8 = totals.loc[totals.groupby(\"line\")[\"entries\"].idxmax()].set_index(\"line\")[\"station\"]\nq8"),
 dict(title="Weekday against weekend",
      task="Mean `entries` per station-day, split by line and by whether the date falls on a Saturday\nor Sunday. Round to whole riders.",
      shape="a DataFrame, 2 rows by 2 columns.",
      solution="merged[\"day_type\"] = np.where(merged[\"date\"].dt.dayofweek >= 5, \"weekend\", \"weekday\")\nq9 = merged.pivot_table(index=\"line\", columns=\"day_type\", values=\"entries\", aggfunc=\"mean\").round(0)\nq9"),
]
for i, q in enumerate(Q, 1):
    q["output"] = O[f"q{i}"]

build(dict(colab_path="intro/practice/pandas_worksheet.ipynb", intro=INTRO, setup=SETUP,
           questions=Q),
      "/mnt/e/iitm course/da2402-26/intro/practice/pandas_worksheet.ipynb")

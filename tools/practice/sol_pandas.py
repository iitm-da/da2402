import numpy as np, pandas as pd
D = "/mnt/e/iitm course/da2402-26/intro/practice/data/"

def show(tag, v):
    print(f"@@{tag}")
    print(repr(v))
    print("@@end")

daily = pd.read_csv(D+"metro_daily.csv", parse_dates=["date"])
stations = pd.read_csv(D+"metro_stations.csv")

q1 = daily.shape
show("q1", q1)

q2 = int((daily["entries"] > 20000).sum())
show("q2", q2)

daily["net"] = daily["entries"] - daily["exits"]
q3 = float(daily["net"].mean().round(2))
show("q3", q3)

q4 = daily.groupby("station")["entries"].sum().sort_values(ascending=False).head(5)
show("q4", q4)

merged = daily.merge(stations, on="station")
q5 = (merged.groupby("line")["fare_collected"].sum() / 1e6).round(2)
show("q5", q5)

merged["month"] = merged["date"].dt.month
q6 = merged.pivot_table(index="month", columns="line", values="entries", aggfunc="sum")
show("q6", q6)

q7 = daily.set_index("date")["entries"].resample("ME").sum()
show("q7", q7)

totals = merged.groupby(["line", "station"])["entries"].sum().reset_index()
q8 = totals.loc[totals.groupby("line")["entries"].idxmax()].set_index("line")["station"]
show("q8", q8)

merged["day_type"] = np.where(merged["date"].dt.dayofweek >= 5, "weekend", "weekday")
q9 = merged.pivot_table(index="line", columns="day_type", values="entries", aggfunc="mean").round(0)
show("q9", q9)

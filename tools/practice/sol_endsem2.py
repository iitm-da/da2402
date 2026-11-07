# Answers to endsem practice paper 2, one block per question, split on "# @@".
# run_endsem.py 2 executes them inside endsem/practice/ and writes out_endsem2.txt.

# @@setup
import os, re, json, sqlite3, io
import requests
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

URL = "https://raw.githubusercontent.com/iitm-da/da2402/master/endsem/practice/data/"

def fetch(name):
    """Download a data file once into ./data/ and return its local path."""
    path = os.path.join("data", name)
    if not os.path.exists(path):
        os.makedirs("data", exist_ok=True)
        r = requests.get(URL + name)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path

# @@q1
wide = pd.read_csv(fetch("p2_store_sales_wide.csv"))
months = wide.columns[1:]
object_cols = [m for m in months if wide[m].dtype == object]

long = wide.melt(id_vars="store", var_name="month", value_name="sales_lakh")
long["sales_lakh"] = pd.to_numeric(long["sales_lakh"], errors="coerce")     # "-" -> NaN
long["month"] = pd.Categorical(long["month"], categories=list(months), ordered=True)

med = long.groupby("store")["sales_lakh"].transform("median")
suspect = long[long["sales_lakh"] > 100 * med]
long.loc[suspect.index, "sales_lakh"] /= 100000                            # rupees -> lakh

long["share"] = long["sales_lakh"] / long.groupby("month", observed=True)["sales_lakh"].transform("sum")
best = long.loc[long.groupby("store")["sales_lakh"].idxmax(), ["store", "month"]]

q1 = {"object_columns": object_cols,
      "missing_after_coerce": int(long["sales_lakh"].isna().sum()),
      "fixed_cell": (suspect["store"].item(), suspect["month"].item()),
      "total_lakh": round(float(long["sales_lakh"].sum()), 2),
      "top_share_Dec": long[long["month"] == "Dec"].nlargest(1, "share")[["store", "share"]]
                       .round(3).values.tolist()[0],
      "best_month": dict(zip(best["store"], best["month"].astype(str)))}
q1

# @@q2
kyc = open(fetch("p2_kyc.txt"), encoding="utf-8").read().splitlines()

FIELD = re.compile(r"PAN: (?P<pan>\S+) \| Mobile: (?P<mobile>\S+) \| "
                   r"Email: (?P<email>.+?) \| PIN: (?P<pin>\S+)$")
RULES = {"pan": r"[A-Z]{5}\d{4}[A-Z]",
         "mobile": r"[6-9]\d{9}",
         "email": r"[\w.+-]+@[\w-]+(\.[\w-]+)*\.[a-z]{2,}",
         "pin": r"[1-9]\d{5}"}

recs = pd.DataFrame([FIELD.search(line).groupdict() for line in kyc])
valid = pd.DataFrame({f: recs[f].map(lambda v, p=p: re.fullmatch(p, v) is not None)
                      for f, p in RULES.items()})

q2 = {"records": len(recs),
      "invalid_per_field": (~valid).sum().to_dict(),
      "fully_valid": int(valid.all(axis=1).sum())}
q2

# @@q3
html = open(fetch("p2_results.html"), encoding="utf-8").read()
t = pd.read_html(io.StringIO(html))[0]
t.columns = ["constituency", "A", "B", "C", "winner"]          # flatten the two header rows

page_total = t[t["constituency"] == "Total"]
t = t[t["constituency"] != "Total"].copy()
t["constituency"] = t["constituency"].str.replace(r"\s*\[\w\]$", "", regex=True)
for c in ["A", "B", "C"]:
    t[c] = pd.to_numeric(t[c].astype(str).str.replace(",", ""), errors="coerce")
    page_total[c] = pd.to_numeric(page_total[c].astype(str).str.replace(",", ""))

q3 = {"seats": len(t),
      "footnote_marks_left": int(t["constituency"].str.contains(r"\[").sum()),
      "not_contested": t.loc[t["C"].isna(), "constituency"].tolist(),
      "totals_match": bool((t[["A", "B", "C"]].sum().to_numpy() == page_total[["A", "B", "C"]]
                            .to_numpy()[0]).all()),
      "seats_won": t["winner"].value_counts().to_dict()}
q3

# @@q4
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.parse(open(fetch("p2_robots.txt")).read().splitlines())

paths = ["/products/kettle", "/cart/checkout", "/account/orders", "/account/help/returns",
         "/products?sort=price", "/accounts"]
q4 = {"can_fetch": {p: rp.can_fetch("MyCrawler", "https://shop.example" + p) for p in paths},
      "crawl_delay": rp.crawl_delay("MyCrawler"),
      "badbot_home": rp.can_fetch("BadBot", "https://shop.example/")}
q4

# @@q5
cursor, pages, raw = "p2_listings_1.json", 0, []
while cursor:
    doc = json.load(open(fetch(cursor), encoding="utf-8"))
    raw.extend(doc["results"])
    pages += 1
    cursor = doc["next_cursor"]

lst = pd.json_normalize(raw)                     # price.amount, seller.name, seller.verified ...
dupes = int(lst["id"].duplicated().sum())
lst = lst.drop_duplicates("id")
tags = lst.explode("tags")

q5 = {"pages": pages, "records_received": len(raw), "duplicates": dupes, "unique": len(lst),
      "columns": sorted(lst.columns),
      "median_price_by_seller": lst.groupby("seller.name")["price.amount"].median().to_dict(),
      "verified_share": round(float(lst["seller.verified"].mean()), 3),
      "no_tags": int(tags["tags"].isna().sum()),
      "top_tag": tags["tags"].value_counts().idxmax()}
q5

# @@q6
staff = pd.read_csv(fetch("p2_staff.csv"))
cols = ["age", "tenure_yrs", "income_k", "spend_k"]

def littles_mcar_test(df, cols):
    means, cov = df[cols].mean(), df[cols].cov()          # available-data estimates
    d2, observed_total = 0.0, 0
    for pattern, idx in df[cols].isna().groupby(cols).groups.items():
        obs = [c for c, miss in zip(cols, pattern) if not miss]
        diff = df.loc[idx, obs].mean() - means[obs]
        d2 += len(idx) * diff @ np.linalg.inv(cov.loc[obs, obs]) @ diff
        observed_total += len(obs)
    dof = observed_total - len(cols)
    return d2, dof, stats.chi2.sf(d2, dof)

d2, dof, p = littles_mcar_test(staff, cols)

y = staff["income_k"].isna().astype(int)
fit = sm.Logit(y, sm.add_constant(staff[["age", "tenure_yrs"]])).fit(disp=0)

q6 = {"patterns": int(staff[cols].isna().drop_duplicates().shape[0]),
      "little_d2": round(float(d2), 2), "df": dof, "little_p": float(f"{p:.3g}"),
      "income_LR_p": float(f"{fit.llr_pvalue:.3g}"),
      "income_wald_p": {k: float(f"{v:.3g}") for k, v in fit.pvalues.items() if k != "const"}}
q6

# @@q7
s = pd.read_csv(fetch("p2_sensor_hourly.csv"), parse_dates=["time"])
truth = pd.read_csv(fetch("p2_sensor_hourly_truth.csv"))["temp_c"]
miss = s["temp_c"].isna()

run = miss.ne(miss.shift()).cumsum()                     # label each run of missing values
gap_len = miss.groupby(run).transform("sum").where(miss, 0)
short, long_ = miss & (gap_len == 1), miss & (gap_len > 1)

fills = {"mean": s["temp_c"].fillna(s["temp_c"].mean()),
         "ffill": s["temp_c"].ffill(),
         "linear": s["temp_c"].interpolate(method="linear"),
         "same hour yesterday": s["temp_c"].fillna(s["temp_c"].shift(24))}

rmse = lambda f, m: round(float(np.sqrt(((f[m] - truth[m]) ** 2).mean())), 3)
q7 = pd.DataFrame({name: {"rmse_single_gaps": rmse(f, short), "rmse_12h_outage": rmse(f, long_)}
                   for name, f in fills.items()}).T
q7

# @@q8
inc = pd.read_csv(fetch("p2_incomes.csv"))
planted = pd.read_csv(fetch("p2_incomes_truth.csv"))["planted"]
x = inc["income_lakh"]

def iqr_flags(v):
    q1, q3 = v.quantile([.25, .75])
    return (v < q1 - 1.5 * (q3 - q1)) | (v > q3 + 1.5 * (q3 - q1))

def modz_flags(v):
    med = v.median()
    return (0.6745 * (v - med) / (v - med).abs().median()).abs() > 3.5

rules = {"IQR raw": iqr_flags(x), "IQR log10": iqr_flags(np.log10(x)),
         "modified z raw": modz_flags(x), "modified z log10": modz_flags(np.log10(x))}
q8 = pd.DataFrame({k: {"flagged": int(f.sum()), "planted_caught": int((f & planted).sum()),
                       "clean_flagged": int((f & ~planted).sum())} for k, f in rules.items()}).T
q8

# @@q9
tx = pd.read_csv(fetch("p2_transactions.csv"))
fraud = pd.read_csv(fetch("p2_transactions_truth.csv"))["fraud"]
Z = StandardScaler().fit_transform(np.c_[tx["hour"], np.log10(tx["amount"])])

iso = IsolationForest(n_estimators=200, contamination=0.02, random_state=42).fit(Z)
db = DBSCAN(eps=0.5, min_samples=8).fit(Z)

def score(flag):
    tp = int((flag & fraud).sum())
    return {"flagged": int(flag.sum()), "true_pos": tp,
            "precision": round(tp / flag.sum(), 3), "recall": round(tp / fraud.sum(), 3)}

q9 = pd.DataFrame({"isolation forest": score(pd.Series(iso.predict(Z) == -1)),
                   "DBSCAN noise": score(pd.Series(db.labels_ == -1))}).T
q9

# @@q10
pairs = pd.read_csv(fetch("p2_pairs.csv"))
match = pd.read_csv(fetch("p2_pairs_truth.csv"))["match"]
m = {"surname": .95, "dob": .9, "pincode": .85, "phone": .8}
u = {"surname": .05, "dob": .003, "pincode": .1, "phone": .001}

weights = pd.DataFrame({f: {"agree": np.log2(m[f] / u[f]),
                            "disagree": np.log2((1 - m[f]) / (1 - u[f]))} for f in m}).T.round(3)
pairs["score"] = sum(np.where(pairs[f] == 1, weights.loc[f, "agree"], weights.loc[f, "disagree"])
                     for f in m)

res = {}
for thr in [0, 5, 10, 14]:
    flag = pairs["score"] > thr
    tp = int((flag & match).sum())
    res[f"> {thr} bits"] = {"flagged": int(flag.sum()), "precision": round(tp / flag.sum(), 3),
                            "recall": round(tp / match.sum(), 3)}
q10 = (weights, pd.DataFrame(res).T)
q10

# @@q11
lines = pd.read_csv(fetch("p2_order_lines.csv"))
products = lines[["product_id", "product", "category", "unit_price"]].drop_duplicates()
order_lines = lines[["line_id", "order_date", "product_id", "qty"]]

con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE products (product_id TEXT PRIMARY KEY, product TEXT,
               category TEXT, unit_price INTEGER)""")
con.execute("""CREATE TABLE order_lines (line_id INTEGER PRIMARY KEY, order_date TEXT,
               product_id TEXT REFERENCES products(product_id), qty INTEGER)""")
products.to_sql("products", con, if_exists="append", index=False)
order_lines.to_sql("order_lines", con, if_exists="append", index=False)

big_months = pd.read_sql("""
    SELECT strftime('%Y-%m', order_date) AS month, SUM(qty * unit_price) AS revenue
    FROM order_lines JOIN products USING (product_id)
    GROUP BY month HAVING revenue > 150000 ORDER BY month""", con)

top_per_cat = pd.read_sql("""
    SELECT category, product, revenue FROM (
        SELECT category, product, SUM(qty * unit_price) AS revenue,
               ROW_NUMBER() OVER (PARTITION BY category ORDER BY SUM(qty * unit_price) DESC) AS rk
        FROM order_lines JOIN products USING (product_id)
        GROUP BY category, product)
    WHERE rk = 1 ORDER BY category""", con)

q11 = {"cells_saved": lines.size - products.size - order_lines.size,
       "months_over_1.5_lakh": big_months["month"].tolist(),
       "top_per_category": dict(zip(top_per_cat["category"], top_per_cat["product"]))}
q11

# @@q12
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px

gm = px.data.gapminder()
app = Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(id="cont", options=sorted(gm["continent"].unique()), value="Asia"),
    dcc.Dropdown(id="country"),
    dcc.Input(id="year", type="number", value=2007),
    html.Button("Show", id="go"),
    html.Div(id="out")])

@app.callback(Output("country", "options"), Output("country", "value"), Input("cont", "value"))
def countries(cont):
    opts = sorted(gm.loc[gm["continent"] == cont, "country"].unique())
    return opts, opts[0]

@app.callback(Output("out", "children"), Input("go", "n_clicks"),
              State("country", "value"), State("year", "value"))
def show(n_clicks, country, year):
    if not n_clicks:
        raise PreventUpdate
    row = gm[(gm["country"] == country) & (gm["year"] == year)]
    if row.empty:
        return f"No Gapminder row for {country} in {year} (data runs 1952-2007 in steps of 5)."
    return f"{country}, {year}: life expectancy {row['lifeExp'].item():.1f} years"

# app.run(jupyter_mode="inline")      # uncomment to see the app
opts, first = countries("Oceania")
try:
    show(None, "India", 2007)
    blocked = False
except PreventUpdate:
    blocked = True
q12 = (opts, first, blocked, show(1, "India", 2007), show(1, "India", 2005))
q12

# @@q13
rec = pd.read_csv(fetch("p2_recovery.csv"))
rec["rate"] = rec["recovered"] / rec["patients"]

overall = rec.groupby("hospital")[["recovered", "patients"]].sum()
overall = (overall["recovered"] / overall["patients"]).round(3).to_dict()
by_sev = rec.pivot(index="severity", columns="hospital", values="rate").round(3)

mix = rec.groupby("severity")["patients"].sum() / rec["patients"].sum()     # pooled case mix
standardised = (by_sev.mul(mix, axis=0).sum()).round(3).to_dict()

# a bubble chart that scales the radius by value: 2x the value draws 4x the area
q13 = {"overall": overall, "by_severity": by_sev.to_dict(), "standardised": standardised,
       "area_ratio_if_radius_scaled_for_2x": 2 ** 2}
q13

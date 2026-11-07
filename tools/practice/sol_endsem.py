# Answers to the endsem practice paper, one block per question, split on "# @@".
# run_endsem.py executes the blocks in order (inside endsem/practice/) and
# writes out_endsem.txt; spec_endsem.py pastes each block and its output.

# @@setup
import os, re, json, sqlite3
import requests
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import LocalOutlierFactor
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
orders = pd.read_csv(fetch("orders.csv"))
customers = pd.read_csv(fetch("customers.csv"))

inner = orders.merge(customers, on="customer_id", how="inner")
dup_id = customers.loc[customers.customer_id.duplicated(), "customer_id"].item()
orphans = ~orders.customer_id.isin(customers.customer_id)

# fix: keep the customer's later row, keep every order, label the unknowns
fixed = orders.merge(customers.drop_duplicates("customer_id", keep="last"),
                     on="customer_id", how="left", validate="many_to_one")
fixed["city"] = fixed["city"].fillna("Unknown")
fixed["quarter"] = pd.to_datetime(fixed["order_date"]).dt.quarter
pivot = fixed.pivot_table(index="city", columns="quarter", values="amount", aggfunc="sum")

q1 = {"orders": len(orders),
      "inner_merge_rows": len(inner),
      "duplicated_customer": dup_id,
      "orphan_orders": int(orphans.sum()),
      "orphan_revenue": round(float(orders.loc[orphans, "amount"].sum()), 2),
      "top_city": pivot.sum(axis=1).idxmax(),
      "top_city_Q4": round(float(pivot.loc[pivot.sum(axis=1).idxmax(), 4]), 2)}
q1

# @@q2
lines = open(fetch("messages.txt"), encoding="utf-8").read().splitlines()

ORDER = re.compile(r"#([A-Z]\d{4})\b")
DATE = re.compile(r"\b(\d{2}[/-](?:\d{2}|[A-Z][a-z]{2})[/-]\d{4})\b")
AMOUNT = re.compile(r"(?:Rs\.?|INR|₹)\s?([\d,]+\.\d{2})")
PIN = re.compile(r"\b(\d{6})\b")

rows = []
for line in lines:
    if not (re.search(r"deliver", line, re.I) and ORDER.search(line)):
        continue                     # OTPs, cancellations, the promo and the survey
    rows.append({"order_id": ORDER.search(line).group(1),
                 "date": DATE.search(line).group(1),
                 "amount": float(AMOUNT.search(line).group(1).replace(",", "")),
                 "pincode": PIN.search(line).group(1)})
deliv = pd.DataFrame(rows)
deliv["date"] = pd.to_datetime(deliv["date"], format="mixed", dayfirst=True)

q2 = {"deliveries": len(deliv),
      "total_amount": round(float(deliv["amount"].sum()), 2),
      "by_month": deliv["date"].dt.month_name().value_counts().to_dict(),
      "top_city_prefix": deliv["pincode"].str[:3].value_counts().idxmax()}
q2

# @@q3
from bs4 import BeautifulSoup

page, rows = "shop_p1.html", []
while page:
    soup = BeautifulSoup(open(fetch(page), encoding="utf-8").read(), "html.parser")
    for card in soup.select("div.card"):
        price = card.select_one("span.price")
        rows.append({
            "id": card["data-id"],
            "title": card.select_one("h3.title").get_text(strip=True),
            "price": float(price.get_text().strip("₹").replace(",", "")) if price else np.nan,
            "rating": float(card.select_one("span.rating").get_text().split()[0]),
            "sponsored": "sponsored" in card["class"],
            "page": page})
    nxt = soup.select_one("a.next")
    page = nxt["href"] if nxt else None

shop = pd.DataFrame(rows)
products = shop.drop_duplicates("id")      # first sighting is the organic card

q3 = (len(shop), len(products), int(products["price"].isna().sum()),
      round(float(products["price"].mean()), 2))
q3

# @@q4
doc = json.load(open(fetch("weather.json"), encoding="utf-8"))
w = pd.json_normalize(doc["stations"], record_path="readings",
                      meta=["id", "name", ["location", "lat"]])

q4 = (w.groupby("name")
       .agg(readings=("time", "size"),
            mean_temp=("temp_c", "mean"),
            rain_missing=("rain_mm", lambda s: int(s.isna().sum())),
            rain_total=("rain_mm", "sum"))
       .round(2))
q4

# @@q5
clinic = pd.read_csv(fetch("clinic.csv"))

def perm_test(df, col, by, n_permutations=5000, seed=0):
    rng = np.random.default_rng(seed)
    m = df[col].isna().to_numpy()
    x = df[by].to_numpy()
    observed = abs(x[m].mean() - x[~m].mean())
    count = 0
    for _ in range(n_permutations):
        mp = rng.permutation(m)
        count += abs(x[mp].mean() - x[~mp].mean()) >= observed
    return observed, (1 + count) / (1 + n_permutations)

def lr_test(df, col, predictors):
    y = df[col].isna().astype(int)
    fit = sm.Logit(y, sm.add_constant(df[predictors])).fit(disp=0)
    return fit.llr, fit.llr_pvalue

table = {}
for col in ["cholesterol", "sleep_hours"]:
    diff, p = perm_test(clinic, col, "age")
    chi2, lr_p = lr_test(clinic, col, ["age", "bmi", "sbp"])
    table[col] = {"missing": int(clinic[col].isna().sum()), "perm_diff_age": round(diff, 3),
                  "perm_p": round(p, 4), "LR_chi2": round(chi2, 2), "LR_p": float(f"{lr_p:.3g}")}
q5 = pd.DataFrame(table).T
q5

# @@q6
truth = pd.read_csv(fetch("clinic_truth.csv"))["cholesterol"]
miss = clinic["cholesterol"].isna()

fills = {"mean": clinic["cholesterol"].fillna(clinic["cholesterol"].mean())}

obs = clinic[~miss]
reg = LinearRegression().fit(obs[["age", "bmi"]], obs["cholesterol"])
r = clinic["cholesterol"].copy()
r[miss] = reg.predict(clinic.loc[miss, ["age", "bmi"]])
fills["regression"] = r

cols = ["age", "bmi", "sbp", "cholesterol"]
mu, sd = clinic[cols].mean(), clinic[cols].std()
k = KNNImputer(n_neighbors=5).fit_transform((clinic[cols] - mu) / sd)
fills["knn"] = pd.Series(k[:, 3] * sd["cholesterol"] + mu["cholesterol"])

def describe(v):
    return {"rmse_filled": np.sqrt(((v[miss] - truth[miss]) ** 2).mean()),
            "mean": v.mean(), "sd": v.std(), "corr_age": v.corr(clinic["age"])}

q6 = pd.DataFrame({"truth": describe(truth),
                   **{name: describe(v) for name, v in fills.items()}}).T.round(3)
q6.loc["truth", "rmse_filled"] = 0.0
q6

# @@q7
t = pd.read_csv(fetch("delivery_times.csv"))
x = t["minutes"]

z = (x - x.mean()) / x.std()
Q1, Q3 = x.quantile([0.25, 0.75])
IQR = Q3 - Q1
med = x.median()
mad = (x - med).abs().median()
mz = 0.6745 * (x - med) / mad

flag = {"z > 3": z.abs() > 3,
        "IQR 1.5": (x < Q1 - 1.5 * IQR) | (x > Q3 + 1.5 * IQR),
        "modified z > 3.5": mz.abs() > 3.5}
q7 = {name: int(f.sum()) for name, f in flag.items()}
q7["mean, sd"] = (round(float(x.mean()), 2), round(float(x.std()), 2))
q7["z misses (slow side)"] = sorted(x[flag["IQR 1.5"] & ~flag["z > 3"] & (x > med)].tolist())
q7

# @@q8
s = pd.read_csv(fetch("sensors.csv"))
X = s[["temp_c", "vibration_mm_s"]].to_numpy()

diff = X - X.mean(axis=0)
d2 = np.einsum("ij,jk,ik->i", diff, np.linalg.inv(np.cov(X, rowvar=False)), diff)
maha = s.loc[d2 > stats.chi2.ppf(0.975, df=2), "reading_id"].tolist()

lof = LocalOutlierFactor(n_neighbors=20).fit(StandardScaler().fit_transform(X))
lof_top5 = s["reading_id"].to_numpy()[np.argsort(lof.negative_outlier_factor_)[:5]].tolist()

q8 = {"mahalanobis": sorted(maha), "lof_top5": lof_top5}
q8

# @@q9
from rapidfuzz.distance import JaroWinkler

mem = pd.read_csv(fetch("members.csv"), dtype={"phone": str})
truth9 = pd.read_csv(fetch("members_truth.csv"))

def clean_name(n):
    n = re.sub(r"\s+", " ", n.lower().strip())
    n = re.sub(r"^dr\.?\s+", "", n)
    if "," in n:                                   # "iyer, priya" -> "priya iyer"
        last, first = [p.strip() for p in n.split(",", 1)]
        n = f"{first} {last}"
    return n

mem["name_c"] = mem["name"].map(clean_name)
mem["phone10"] = mem["phone"].str.replace(r"\D", "", regex=True).str[-10:]
mem = mem.merge(truth9, on="record_id")

n = len(mem)
pairs = mem.merge(mem, on="city", suffixes=("_a", "_b"))          # block on city
pairs = pairs[pairs["record_id_a"] < pairs["record_id_b"]].copy()
pairs["jw"] = [JaroWinkler.similarity(a, b) for a, b in zip(pairs["name_c_a"], pairs["name_c_b"])]
pairs["same"] = pairs["person_id_a"] == pairs["person_id_b"]
true_pairs = int((mem.groupby("person_id").size().apply(lambda k: k * (k - 1) // 2)).sum())

rules = {"raw phone equal": pairs["phone_a"] == pairs["phone_b"],
         "clean phone equal": pairs["phone10_a"] == pairs["phone10_b"],
         "name jw >= 0.93": pairs["jw"] >= 0.93,
         "clean phone or name jw >= 0.97": (pairs["phone10_a"] == pairs["phone10_b"]) | (pairs["jw"] >= 0.97)}
res = {}
for name, hit in rules.items():
    tp = int((hit & pairs["same"]).sum())
    res[name] = {"predicted": int(hit.sum()), "true_pos": tp,
                 "precision": round(tp / hit.sum(), 3), "recall": round(tp / true_pairs, 3)}
q9 = (n * (n - 1) // 2, len(pairs), true_pairs, pd.DataFrame(res).T)
q9

# @@q10
a = pd.read_csv(fetch("meters.csv"))
b = pd.read_parquet(fetch("meters.parquet"))

q10 = pd.DataFrame({"csv": a.dtypes.astype(str), "parquet": b.dtypes.astype(str)})
q10.loc["first meter_id"] = [str(a["meter_id"].iloc[0]), str(b["meter_id"].iloc[0])]
q10

# @@q11
con = sqlite3.connect(fetch("shop.db"))

by_city = pd.read_sql("""
    SELECT c.city, COUNT(*) AS orders, SUM(o.qty * p.price) AS revenue
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN products  p ON p.product_id  = o.product_id
    GROUP BY c.city
    ORDER BY revenue DESC""", con)

never = pd.read_sql("""
    SELECT c.customer_id FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.order_id IS NULL ORDER BY c.customer_id""", con)

unsold = pd.read_sql("""
    SELECT p.product FROM products p
    WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.product_id = p.product_id)""", con)

q11 = {"top_city": by_city.loc[0, "city"], "top_revenue": int(by_city.loc[0, "revenue"]),
       "never_ordered": never["customer_id"].tolist(), "unsold": unsold["product"].tolist()}
q11

# @@q12
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

gm = px.data.gapminder()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([dcc.Dropdown(id="continent", options=sorted(gm["continent"].unique()),
                              value="Asia", clearable=False),
                 html.H4(id="kpi", className="mt-3")], md=4),
        dbc.Col(dcc.Graph(id="trend"), md=8)])
], fluid=True)

@app.callback(Output("kpi", "children"), Output("trend", "figure"),
              Input("continent", "value"))
def update(continent):
    med = (gm[gm["continent"] == continent]
           .groupby("year", as_index=False)["lifeExp"].median())
    kpi = f"{continent}: median life expectancy {med['lifeExp'].iloc[-1]:.1f} years in 2007"
    fig = px.line(med, x="year", y="lifeExp", markers=True,
                  title=f"Median life expectancy, {continent}")
    return kpi, fig

# app.run(jupyter_mode="inline")      # uncomment to see the app
kpi, fig = update("Africa")
q12 = (kpi, [round(float(v), 1) for v in fig.data[0].y[:3]], len(fig.data[0].x))
q12

# @@q13
e = pd.read_csv(fetch("enrolment.csv"))
tn = e[e["state"] == "Tamil Nadu"].set_index("year")["enrolled_lakh"]

baseline = 10.0                                  # where the published axis started
shown = (tn[2025] - baseline) / (tn[2024] - baseline) - 1
actual = tn[2025] / tn[2024] - 1

e25 = e[e["year"] == 2025].assign(
    per_1000=lambda d: (d["enrolled_lakh"] / d["population_lakh"] * 1000).round(1))
honest = px.bar(e25.sort_values("per_1000"), x="per_1000", y="state", orientation="h",
                title="Enrolled per 1,000 people, 2025")

q13 = {"shown_change_%": round(float(100 * shown), 1),
       "actual_change_%": round(float(100 * actual), 1),
       "lie_factor": round(float(shown / actual), 1),
       "top_by_count": e25.loc[e25["enrolled_lakh"].idxmax(), "state"],
       "top_per_1000": e25.loc[e25["per_1000"].idxmax(), "state"],
       "per_1000": dict(zip(e25["state"], e25["per_1000"]))}
q13

#!/usr/bin/env python3
"""Write every data file practice paper 2 loads. Seeded; files are prefixed p2_.
Run from this folder:  python3 make_data2.py
"""
import json
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda name: os.path.join(HERE, "p2_" + name)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------- Q1 wide sales
def q1():
    rng = np.random.default_rng(201)
    stores = ["Adyar", "Anna Nagar", "T Nagar", "Velachery", "Porur", "Tambaram", "OMR", "Mylapore"]
    base = rng.uniform(8, 20, len(stores))
    season = 1 + 0.25 * np.sin(np.arange(12) / 12 * 2 * np.pi - 1.2)
    vals = np.round(base[:, None] * season[None, :] * rng.normal(1, .08, (8, 12)), 2)
    df = pd.DataFrame(vals, columns=MONTHS).astype(object)
    df.insert(0, "store", stores)
    # Porur opened in April; the export writes "-" for months it had no sales
    df.loc[df.store == "Porur", ["Jan", "Feb", "Mar"]] = "-"
    # OMR's July figure was keyed in rupees, not lakh
    df.loc[df.store == "OMR", "Jul"] = round(float(vals[6, 6]) * 100000, 0)
    df.to_csv(P("store_sales_wide.csv"), index=False)


# ------------------------------------------------------- Q2 KYC regex
def q2():
    rng = np.random.default_rng(202)
    first = ["Arjun", "Meera", "Farhan", "Lakshmi", "Rohit", "Sneha", "Vivek", "Ananya", "Imran", "Divya"]
    last = ["Sharma", "Iyer", "Khan", "Nair", "Gupta", "Reddy", "Das", "Pillai"]
    L = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rows = []
    for i in range(80):
        f, l = rng.choice(first), rng.choice(last)
        pan = "".join(rng.choice(list(L), 3)) + "P" + l[0] + f"{rng.integers(0, 10000):04d}" + rng.choice(list(L))
        mob = f"{rng.choice([9, 8, 7, 6])}{rng.integers(0, 10**9):09d}"
        email = f"{f.lower()}.{l.lower()}{rng.integers(1, 99)}@{rng.choice(['gmail.com', 'yahoo.co.in', 'iitm.ac.in'])}"
        pin = f"{rng.integers(1, 9)}{rng.integers(0, 10**5):05d}"
        r = rng.random()
        if r < .08: pan = pan[:9]                                  # one character short
        elif r < .14: pan = pan.lower()                            # typed in lower case
        r = rng.random()
        if r < .07: mob = "5" + mob[1:]                            # Indian mobiles start 6-9
        elif r < .12: mob = mob[:9]
        r = rng.random()
        if r < .06: email = email.replace("@", " at ")
        elif r < .10: email = email.replace(".com", ".c")
        if rng.random() < .05: pin = "0" + pin[1:]                 # no PIN code starts with 0
        rows.append(f"{f} {l} | PAN: {pan} | Mobile: {mob} | Email: {email} | PIN: {pin}")
    open(P("kyc.txt"), "w", encoding="utf-8").write("\n".join(rows) + "\n")


# --------------------------------------------------- Q3 HTML results table
def q3():
    rng = np.random.default_rng(203)
    seats = ["Chennai North", "Chennai South", "Chennai Central", "Sriperumbudur", "Kancheepuram",
             "Arakkonam", "Vellore", "Krishnagiri", "Dharmapuri", "Tiruvannamalai", "Arani", "Villupuram"]
    parties = ["Party A", "Party B", "Party C"]
    rows, tot = [], np.zeros(3, int)
    for k, s in enumerate(seats):
        v = (rng.dirichlet([5, 4, 2]) * rng.integers(900000, 1500000)).astype(int)
        tot += v
        def ind(n):
            s_ = f"{n:,}"
            head, tail = s_.replace(",", "")[:-3], s_.replace(",", "")[-3:]
            out = ""
            while len(head) > 2:
                out = "," + head[-2:] + out
                head = head[:-2]
            return (head + out + "," + tail) if head else tail
        name = s + ("<sup>[a]</sup>" if k in (2, 7) else "")
        winner = parties[int(np.argmax(v))]
        cells = [ind(int(x)) for x in v]
        if k == 5:
            cells[2] = "—"            # Party C did not contest Arakkonam
            tot[2] -= v[2]
            v[2] = 0
        rows.append(f"<tr><td>{name}</td>" + "".join(f"<td>{c}</td>" for c in cells) +
                    f"<td>{winner}</td></tr>")
    rows.append("<tr><td><b>Total</b></td>" + "".join(f"<td><b>{t:,}</b></td>" for t in tot) +
                "<td></td></tr>")
    html = ("<!doctype html><html><head><meta charset='utf-8'><title>Results</title></head><body>\n"
            "<h2>Constituency results</h2>\n<table class='results'>\n<thead>"
            "<tr><th rowspan='2'>Constituency</th><th colspan='3'>Votes</th><th rowspan='2'>Winner</th></tr>"
            "<tr><th>Party A</th><th>Party B</th><th>Party C</th></tr></thead>\n<tbody>\n" +
            "\n".join(rows) + "\n</tbody></table>\n"
            "<p><sup>[a]</sup> Recount ordered; figures are provisional.</p>\n</body></html>\n")
    open(P("results.html"), "w", encoding="utf-8").write(html)


# -------------------------------------------------------------- Q4 robots
def q4():
    txt = """# robots.txt for shop.example
User-agent: *
Disallow: /cart/
Disallow: /account
Allow: /account/help
Disallow: /*?sort=
Crawl-delay: 5

User-agent: BadBot
Disallow: /
"""
    open(P("robots.txt"), "w").write(txt)


# --------------------------------------------------- Q5 paged API responses
def q5():
    rng = np.random.default_rng(205)
    recs = []
    for i in range(1, 58):
        recs.append({"id": 5000 + i,
                     "title": f"Listing {i}",
                     "price": {"amount": int(rng.integers(8, 90)) * 1000, "currency": "INR"},
                     "seller": {"name": rng.choice(["Ravi Motors", "City Cars", "AutoHub"]),
                                "verified": bool(rng.random() < .7)},
                     "tags": list(rng.choice(["diesel", "petrol", "cng", "automatic", "first-owner"],
                                             int(rng.integers(0, 3)), replace=False))})
    pages = [recs[0:20], recs[19:40], recs[40:57]]     # record 20 sits on both page 1 and page 2
    for k, pg in enumerate(pages, 1):
        doc = {"page": k, "count": len(pg), "results": pg,
               "next_cursor": f"p2_listings_{k + 1}.json" if k < 3 else None}
        json.dump(doc, open(P(f"listings_{k}.json"), "w"), indent=1)


# ------------------------------------------------- Q6 Little's test data
def q6():
    rng = np.random.default_rng(206)
    n = 400
    age = np.round(rng.uniform(20, 70, n)).astype(int)
    tenure = np.round(np.clip(0.3 * (age - 20) + rng.normal(0, 4, n), 0, None), 1)
    income = np.round(18 + 0.9 * age + 1.2 * tenure + rng.normal(0, 12, n), 1)
    spend = np.round(4 + 0.35 * income + rng.normal(0, 6, n), 1)
    df = pd.DataFrame({"age": age, "tenure_yrs": tenure, "income_k": income, "spend_k": spend})
    # income: MAR on tenure (long-tenure staff skip the question)
    p = 1 / (1 + np.exp(-(-3.4 + 0.18 * tenure)))
    df.loc[rng.random(n) < p, "income_k"] = np.nan
    # spend: MCAR 8%
    df.loc[np.random.default_rng(66).random(n) < .08, "spend_k"] = np.nan
    df.to_csv(P("staff.csv"), index=False)


# ------------------------------------------------- Q7 time-series gaps
def q7():
    rng = np.random.default_rng(207)
    t = pd.date_range("2026-10-01", periods=24 * 7, freq="h")
    h = np.arange(len(t))
    temp = 27 + 4 * np.sin((h % 24 - 9) / 24 * 2 * np.pi) + np.cumsum(rng.normal(0, .15, len(t)))
    temp = np.round(temp, 2)
    truth = pd.DataFrame({"time": t, "temp_c": temp})
    obs = truth.copy()
    gaps = list(rng.choice(np.arange(5, 150), 14, replace=False))
    for g in gaps:
        obs.loc[g, "temp_c"] = np.nan                                   # single dropped readings
    obs.loc[100:111, "temp_c"] = np.nan                                 # 12-hour outage
    obs.to_csv(P("sensor_hourly.csv"), index=False)
    truth.to_csv(P("sensor_hourly_truth.csv"), index=False)


# ------------------------------------------------ Q8 skewed incomes
def q8():
    rng = np.random.default_rng(208)
    inc = np.round(np.exp(rng.normal(np.log(6.5), 0.55, 495)), 2)      # lakh per year
    errors = np.array([0.0065, 0.0081, 650.0, 812.0, 5.5e3])           # unit slips and a junk entry
    x = np.concatenate([inc, errors])
    planted = np.r_[np.zeros(495, bool), np.ones(5, bool)]
    idx = rng.permutation(500)
    pd.DataFrame({"household": np.arange(1, 501), "income_lakh": x[idx]}).to_csv(
        P("incomes.csv"), index=False)
    pd.DataFrame({"household": np.arange(1, 501), "planted": planted[idx]}).to_csv(
        P("incomes_truth.csv"), index=False)


# ----------------------------------------- Q9 multivariate: card transactions
def q9():
    rng = np.random.default_rng(209)
    n = 600
    hour = np.clip(rng.normal(15, 3.5, n), 6, 23.9)
    amount = np.exp(rng.normal(np.log(900), .5, n)) * (1 + .03 * (hour - 15))
    fraud_hour = rng.uniform(1.5, 4.5, 9)
    fraud_amt = rng.uniform(15000, 40000, 9)
    small_night = np.c_[rng.uniform(2, 4, 3), rng.uniform(300, 900, 3)]   # odd hour, normal amount
    H = np.r_[hour, fraud_hour, small_night[:, 0]]
    A = np.r_[amount, fraud_amt, small_night[:, 1]]
    lab = np.r_[np.zeros(n, bool), np.ones(12, bool)]
    idx = rng.permutation(len(H))
    df = pd.DataFrame({"txn_id": np.arange(1, len(H) + 1), "hour": np.round(H[idx], 2),
                       "amount": np.round(A[idx], 0)})
    df.to_csv(P("transactions.csv"), index=False)
    pd.DataFrame({"txn_id": df.txn_id, "fraud": lab[idx]}).to_csv(P("transactions_truth.csv"), index=False)


# ---------------------------------------------- Q10 Fellegi-Sunter pairs
def q10():
    rng = np.random.default_rng(210)
    m = {"surname": .95, "dob": .9, "pincode": .85, "phone": .8}
    u = {"surname": .05, "dob": .003, "pincode": .1, "phone": .001}
    rows = []
    for _ in range(112):                      # matches, agreeing at the m rates
        rows.append(dict({f: int(rng.random() < m[f]) for f in m}, match=True))
    for _ in range(8):                        # matches who moved and changed phone
        rows.append(dict(surname=1, dob=1, pincode=0, phone=0, match=True))
    for _ in range(268):                      # non-matches, agreeing at the u rates
        rows.append(dict({f: int(rng.random() < u[f]) for f in m}, match=False))
    for _ in range(12):                       # family members: same surname, home and landline
        rows.append(dict(surname=1, dob=0, pincode=1, phone=1, match=False))
    df = pd.DataFrame(rows).sample(frac=1, random_state=10).reset_index(drop=True)
    df.insert(0, "pair_id", np.arange(1, len(df) + 1))
    df[["pair_id", *m]].to_csv(P("pairs.csv"), index=False)
    df[["pair_id", "match"]].to_csv(P("pairs_truth.csv"), index=False)


# ------------------------------------------- Q11 denormalised order lines
def q11():
    rng = np.random.default_rng(211)
    prods = [("P01", "Steel Bottle", "Kitchen", 349), ("P02", "Kettle", "Kitchen", 1299),
             ("P03", "Tawa", "Kitchen", 899), ("P04", "Notebook", "Stationery", 79),
             ("P05", "Gel Pen Set", "Stationery", 149), ("P06", "Planner", "Stationery", 499),
             ("P07", "Earphones", "Electronics", 999), ("P08", "Power Bank", "Electronics", 1499),
             ("P09", "Charger", "Electronics", 699)]
    rows = []
    for i in range(1, 501):
        p = prods[int(rng.choice(9, p=[.14, .06, .1, .2, .12, .05, .12, .08, .13]))]
        rows.append({"line_id": i, "order_date": str(pd.Timestamp("2025-07-01") +
                                                       pd.Timedelta(days=int(rng.integers(0, 184))))[:10],
                     "product_id": p[0], "product": p[1], "category": p[2], "unit_price": p[3],
                     "qty": int(rng.integers(1, 6))})
    pd.DataFrame(rows).to_csv(P("order_lines.csv"), index=False)


# ------------------------------------------------- Q13 Simpson's paradox
def q13():
    rows = [("City Hospital", "mild", 600, 570), ("City Hospital", "severe", 400, 280),
            ("Town Clinic", "mild", 900, 828), ("Town Clinic", "severe", 100, 60)]
    pd.DataFrame(rows, columns=["hospital", "severity", "patients", "recovered"]).to_csv(
        P("recovery.csv"), index=False)


if __name__ == "__main__":
    for f in (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q13):
        f()
    print(sorted(x for x in os.listdir(HERE) if x.startswith("p2_")))

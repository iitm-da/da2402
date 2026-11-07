#!/usr/bin/env python3
"""Write every data file the endsem practice paper loads.

Seeded, so re-running reproduces the exact files the pasted answers were
computed from. Each question's defects are planted here by construction.
Run from this folder:  python3 make_data.py
"""
import json
import sqlite3
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda name: os.path.join(HERE, name)
CITIES = ["Chennai", "Bengaluru", "Hyderabad", "Pune", "Kochi", "Coimbatore"]


# ---------------------------------------------------------------- Q1 pandas
def q1():
    rng = np.random.default_rng(2402)
    cust = pd.DataFrame({"customer_id": np.arange(1, 151),
                         "city": rng.choice(CITIES, 150, p=[.25, .22, .18, .15, .1, .1])})
    # customer 42 moved, and the CRM kept both rows
    old_city = cust.loc[cust.customer_id == 42, "city"].item()
    new_city = "Coimbatore" if old_city != "Coimbatore" else "Kochi"
    cust = pd.concat([cust, pd.DataFrame({"customer_id": [42], "city": [new_city]})],
                     ignore_index=True)
    n = 1200
    ids = rng.integers(1, 151, n)
    ids[rng.choice(n, 9, replace=False)] = rng.choice([151, 152, 153], 9)  # not in customers
    ids[rng.choice(np.where(ids <= 150)[0], 6, replace=False)] = 42
    dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), "D")
    orders = pd.DataFrame({"order_id": np.arange(10001, 10001 + n), "customer_id": ids,
                           "order_date": dates.strftime("%Y-%m-%d"),
                           "amount": np.round(rng.gamma(2.2, 420, n), 2)})
    orders.sort_values("order_date").to_csv(P("orders.csv"), index=False)
    cust.to_csv(P("customers.csv"), index=False)


# ----------------------------------------------------------------- Q2 regex
def q2():
    rng = np.random.default_rng(7)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    lines = []
    for i in range(60):
        oid = f"{rng.choice(list('ABKZ'))}{rng.integers(1000, 9999)}"
        pin = f"{rng.choice([600, 560, 500, 411, 682])}{rng.integers(0, 100):03d}"
        d, m = int(rng.integers(1, 29)), int(rng.integers(8, 11))
        amt = float(np.round(rng.gamma(2, 600), 2))
        amt_s = f"{amt:,.2f}" if rng.random() < .6 else f"{amt:.2f}"
        cur = rng.choice(["Rs.", "Rs", "INR", "₹"])
        sep = "" if cur == "₹" else " "
        date = f"{d:02d}/{m:02d}/2026" if rng.random() < .5 else f"{d:02d}-{months[m-1]}-2026"
        tmpl = rng.integers(0, 3)
        if tmpl == 0:
            s = f"Order #{oid} delivered to {pin} on {date}. Paid {cur}{sep}{amt_s}"
        elif tmpl == 1:
            s = f"Your order #{oid} for {cur}{sep}{amt_s} was delivered on {date} (PIN {pin})"
        else:
            s = f"DELIVERED: #{oid} | {date} | {cur}{sep}{amt_s} | pincode {pin}"
        lines.append(s)
    noise = [f"{rng.integers(100000, 999999)} is your OTP. Do not share it. Valid till 10 min."
             for _ in range(8)]
    noise += [f"Order #{rng.choice(list('ABKZ'))}{rng.integers(1000, 9999)} cancelled on "
              f"{int(rng.integers(1,29)):02d}/10/2026. Refund of Rs. {rng.integers(100, 900)}.00 initiated"
              for _ in range(5)]
    noise += ["Flat 50% off today only! Use code SAVE50 at checkout.",
              "Rate your delivery on 12/10/2026 and win Rs. 500"]
    allx = lines + noise
    order = rng.permutation(len(allx))
    with open(P("messages.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(allx[i] for i in order) + "\n")


# -------------------------------------------------------------- Q3 scraping
CARD = ('  <div class="card{extra}" data-id="{pid}">\n    <h3 class="title">{title}</h3>\n'
        '    {price}\n    <span class="rating">{rating} ★</span>\n  </div>\n')


def q3():
    rng = np.random.default_rng(31)
    kinds = ["Steel Bottle", "Desk Lamp", "Yoga Mat", "Backpack", "Kettle", "Notebook Set",
             "Wall Clock", "Earphones", "Lunch Box", "Umbrella", "Mouse Pad", "Plant Pot"]
    prods = []
    for i, k in enumerate(kinds * 3):
        prods.append(dict(pid=f"P{101 + i}", title=f"{k} {['Mini', 'Classic', 'Pro'][i // 12]}",
                          price=int(rng.integers(199, 2999)),
                          rating=float(np.round(rng.uniform(3.1, 4.9), 1))))
    prods = prods[:32]
    for i in (5, 19):            # out of stock: no price span at all
        prods[i]["price"] = None
    pages = [prods[0:12], prods[12:24], prods[24:32]]

    def card(p, sponsored=False):
        price = ('<span class="price">₹{:,}</span>'.format(p["price"]) if p["price"]
                 else '<span class="stock">Out of stock</span>')
        return CARD.format(extra=" sponsored" if sponsored else "", pid=p["pid"],
                           title=p["title"], price=price, rating=p["rating"])
    for k, pg in enumerate(pages, 1):
        body = "".join(card(p) for p in pg)
        if k == 2:                       # a sponsored repeat of a page-1 product
            body = card(prods[3], sponsored=True) + body
        if k == 3:
            body += card(prods[14], sponsored=True)
        nxt = f'<a class="next" href="shop_p{k + 1}.html">Next ›</a>' if k < 3 else ""
        html = (f"<!doctype html>\n<html><head><meta charset='utf-8'><title>Shop · page {k}</title>"
                f"</head>\n<body>\n<div class=\"grid\">\n{body}</div>\n"
                f"<nav><span>Page {k} of 3</span> {nxt}</nav>\n</body></html>\n")
        open(P(f"shop_p{k}.html"), "w", encoding="utf-8").write(html)


# ------------------------------------------------------------------ Q4 JSON
def q4():
    rng = np.random.default_rng(44)
    stations = []
    for sid, name, lat, lon in [("ST01", "Guindy", 13.01, 80.21), ("ST02", "Adyar", 13.00, 80.26),
                                ("ST03", "Tambaram", 12.92, 80.12), ("ST04", "Ennore", 13.21, 80.32)]:
        reads = []
        for h in range(0, 24, 3):
            r = {"time": f"2026-11-01T{h:02d}:00", "temp_c": float(np.round(rng.normal(28, 2.2), 1))}
            if rng.random() > .25:
                r["rain_mm"] = float(np.round(rng.gamma(1.2, 3), 1))
            reads.append(r)
        if sid == "ST04":
            reads = reads[:5]          # station went offline
        stations.append({"id": sid, "name": name, "location": {"lat": lat, "lon": lon},
                         "readings": reads})
    doc = {"city": "Chennai", "fetched": "2026-11-02T06:00:00+05:30",
           "units": {"temp": "C", "rain": "mm"}, "stations": stations}
    json.dump(doc, open(P("weather.json"), "w"), indent=2)


# ----------------------------------------------------- Q5, Q6 missing data
def q56():
    rng = np.random.default_rng(56)
    n = 500
    age = np.round(rng.uniform(22, 78, n)).astype(int)
    bmi = np.round(rng.normal(25.5, 4, n), 1)
    sbp = np.round(100 + 0.55 * age + 0.9 * (bmi - 25) + rng.normal(0, 9, n)).astype(int)
    chol = np.round(120 + 1.4 * age + 2.2 * (bmi - 25) + rng.normal(0, 22, n), 1)
    sleep = np.round(rng.normal(6.8, 1.0, n), 1)
    df = pd.DataFrame({"patient_id": np.arange(1, n + 1), "age": age, "bmi": bmi, "sbp": sbp,
                       "cholesterol": chol, "sleep_hours": sleep})
    truth = df[["patient_id", "cholesterol"]].copy()
    # cholesterol: MAR, older patients more often skip the fasting test
    p = 1 / (1 + np.exp(-(-4.2 + 0.06 * age)))
    df.loc[rng.random(n) < p, "cholesterol"] = np.nan
    # sleep_hours: MCAR, a flat 10% of forms left it blank
    df.loc[np.random.default_rng(3).random(n) < .10, "sleep_hours"] = np.nan
    df.to_csv(P("clinic.csv"), index=False)
    truth.to_csv(P("clinic_truth.csv"), index=False)


# ------------------------------------------------------ Q7 univariate outliers
def q7():
    rng = np.random.default_rng(77)
    base = np.round(rng.normal(32, 6, 282), 1)
    # a stalled batch: eighteen orders stuck at the hub for 1.5-3 hours
    stuck = np.round(rng.uniform(85, 170, 18), 1)
    mins = np.concatenate([base, stuck])
    idx = rng.permutation(len(mins))
    pd.DataFrame({"order_id": np.arange(1, 301), "minutes": mins[idx]}).to_csv(
        P("delivery_times.csv"), index=False)


# ---------------------------------------------------- Q8 multivariate outliers
def q8():
    rng = np.random.default_rng(88)
    a = rng.multivariate_normal([40, 2.0], [[4, 0.3], [0.3, 0.04]], 160)   # machine A, tight
    b = rng.multivariate_normal([70, 6.0], [[36, 2.0], [2.0, 1.0]], 140)   # machine B, loose
    planted = np.array([[48.5, 3.6],     # just off A's tight cloud: a local outlier
                        [55.0, 4.0],     # between the machines
                        [95.0, 1.0]])    # far from everything
    X = np.vstack([a, b, planted])
    machine = ["A"] * 160 + ["B"] * 140 + ["?"] * 3
    idx = rng.permutation(len(X))
    df = pd.DataFrame({"reading_id": np.arange(1, len(X) + 1), "temp_c": np.round(X[idx, 0], 2),
                       "vibration_mm_s": np.round(X[idx, 1], 3)})
    df.to_csv(P("sensors.csv"), index=False)
    planted_ids = [int(df.reading_id[np.where(idx == 300 + k)[0][0]]) for k in range(3)]
    return planted_ids


# --------------------------------------------------------------- Q9 dedup
FIRST = ["Priya", "Karthik", "Anitha", "Rahul", "Divya", "Suresh", "Meena", "Arjun", "Lakshmi",
         "Vikram", "Deepa", "Ganesh", "Kavya", "Manoj", "Nithya", "Sanjay", "Revathi", "Ashok",
         "Swathi", "Harish"]
LAST = ["Raman", "Iyer", "Krishnan", "Menon", "Reddy", "Nair", "Subramanian", "Pillai", "Rao",
        "Kumar", "Srinivasan", "Natarajan"]


def q9():
    rng = np.random.default_rng(99)
    people = []
    seen = set()
    while len(people) < 160:
        f, l = rng.choice(FIRST), rng.choice(LAST)
        if (f, l) in seen and rng.random() < .7:
            continue
        seen.add((f, l))
        phone = f"{rng.choice([9, 8, 7])}{rng.integers(100000000, 999999999)}"
        people.append(dict(first=f, last=l, phone=phone, city=rng.choice(CITIES[:4])))

    def fmt_phone(p, style):
        return [p, f"+91 {p[:5]} {p[5:]}", f"+91-{p}", f"0{p}"][style]

    def mess_name(f, l, r):
        k = r.integers(0, 5)
        if k == 0: return f"{f} {l}".upper()
        if k == 1: return f"  {f}  {l} "
        if k == 2: return f"Dr. {f} {l}"
        if k == 3:                                  # one-letter typo
            j = int(r.integers(1, len(l) - 1))
            return f"{f} {l[:j]}{l[j + 1:]}"
        return f"{l}, {f}"

    rows = []
    for pid, p in enumerate(people, 1):
        rows.append(dict(person_id=pid, name=f"{p['first']} {p['last']}",
                         phone=fmt_phone(p["phone"], 0), city=p["city"]))
        ncopies = rng.choice([0, 1, 2], p=[.7, .22, .08])
        for _ in range(ncopies):
            ph = p["phone"]
            if rng.random() < .15:            # signed up again with a new number
                ph = f"{rng.choice([9, 8, 7])}{rng.integers(100000000, 999999999)}"
            rows.append(dict(person_id=pid, name=mess_name(p["first"], p["last"], rng),
                             phone=fmt_phone(ph, int(rng.integers(1, 4))),
                             city=p["city"]))
    df = pd.DataFrame(rows).sample(frac=1, random_state=9).reset_index(drop=True)
    df.insert(0, "record_id", np.arange(1, len(df) + 1))
    df[["record_id", "name", "phone", "city"]].to_csv(P("members.csv"), index=False)
    df[["record_id", "person_id"]].to_csv(P("members_truth.csv"), index=False)


# -------------------------------------------------------------- Q10 storage
def q10():
    rng = np.random.default_rng(1010)
    n = 400
    meters = pd.DataFrame({
        "meter_id": [f"{x:06d}" for x in rng.integers(1, 30000, n)],
        "read_on": (pd.Timestamp("2026-06-01") + pd.to_timedelta(rng.integers(0, 120, n), "D"))
        .strftime("%Y-%m-%d"),
        "zone": rng.choice(["North", "South", "Central"], n),
        "units": np.round(rng.gamma(3, 60, n), 1)})
    meters.to_csv(P("meters.csv"), index=False)
    m2 = meters.assign(read_on=pd.to_datetime(meters.read_on),
                       zone=meters.zone.astype("category"))
    m2.to_parquet(P("meters.parquet"), index=False)

    if os.path.exists(P("shop.db")):
        os.remove(P("shop.db"))
    con = sqlite3.connect(P("shop.db"))
    cust = pd.DataFrame({"customer_id": np.arange(1, 81),
                         "name": [f"Customer {i:02d}" for i in range(1, 81)],
                         "city": rng.choice(CITIES, 80)})
    prods = pd.DataFrame({"product_id": np.arange(1, 21),
                          "product": [f"Item {chr(65 + i)}" for i in range(20)],
                          "category": rng.choice(["Kitchen", "Stationery", "Electronics", "Garden"], 20),
                          "price": rng.integers(50, 2500, 20)})
    buyers = rng.choice(np.setdiff1d(np.arange(1, 81), [7, 23, 51, 64, 78]), 900)
    items = rng.choice(np.setdiff1d(np.arange(1, 21), [12, 17]), 900)
    orders = pd.DataFrame({"order_id": np.arange(1, 901), "customer_id": buyers,
                           "product_id": items, "qty": rng.integers(1, 5, 900),
                           "order_date": (pd.Timestamp("2025-01-01") +
                                          pd.to_timedelta(rng.integers(0, 365, 900), "D"))
                           .strftime("%Y-%m-%d")})
    cust.to_sql("customers", con, index=False)
    prods.to_sql("products", con, index=False)
    orders.to_sql("orders", con, index=False)
    con.commit()
    con.close()


# ------------------------------------------------------------ Q12 charts
def q12():
    rows = [("Tamil Nadu", 2024, 10.21, 772), ("Tamil Nadu", 2025, 10.62, 776),
            ("Kerala", 2024, 4.48, 357), ("Kerala", 2025, 4.55, 358),
            ("Karnataka", 2024, 8.90, 683), ("Karnataka", 2025, 9.18, 688),
            ("Telangana", 2024, 5.95, 382), ("Telangana", 2025, 6.31, 385),
            ("Goa", 2024, 0.32, 16), ("Goa", 2025, 0.34, 16)]
    pd.DataFrame(rows, columns=["state", "year", "enrolled_lakh", "population_lakh"]).to_csv(
        P("enrolment.csv"), index=False)


if __name__ == "__main__":
    q1(); q2(); q3(); q4(); q56(); q7()
    print("q8 planted reading_ids:", q8())
    q9(); q10(); q12()
    print("written:", sorted(os.listdir(HERE)))

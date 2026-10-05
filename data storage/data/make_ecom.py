# Writes ecom.db: a small shop database for the SQLite lecture.
# customers, products, orders. One row in orders is one item sold.
# Ported from the 2025 MySQL version, with a seed so every number reproduces.
import os
import sqlite3
import numpy as np
import pandas as pd

rng = np.random.default_rng(2402)
DB = 'ecom.db'
if os.path.exists(DB):
    os.remove(DB)

# ---- customers ---------------------------------------------------------
first = ['Aarav', 'Priya', 'Karthik', 'Divya', 'Rahul', 'Ananya', 'Vikram', 'Sneha',
         'Arjun', 'Meera', 'Rohan', 'Kavya', 'Siddharth', 'Lakshmi', 'Imran', 'Fatima',
         'Harish', 'Pooja', 'Naveen', 'Ishita']
last = ['Sharma', 'Iyer', 'Reddy', 'Nair', 'Gupta', 'Menon', 'Das', 'Khan',
        'Patel', 'Rao', 'Singh', 'Bose', 'Pillai', 'Joshi', 'Mehta']
places = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore']
n_cust = 100
names = [f'{rng.choice(first)} {rng.choice(last)}' for _ in range(n_cust)]
customers = pd.DataFrame({
    'customer_id': range(1, n_cust + 1),
    'name': names,
    'email': [f"{n.split()[0].lower()}.{n.split()[1].lower()}{i}@example.com"
              for i, n in enumerate(names, 1)],
    'place': rng.choice(places, n_cust, p=[.26, .24, .2, .12, .18]),
})

# ---- products ----------------------------------------------------------
catalogue = {
    'Snacks':      (['Masala Chips', 'Banana Chips', 'Murukku', 'Mixture', 'Peanut Chikki',
                     'Khakhra', 'Bhujia', 'Nachos', 'Popcorn', 'Mathri', 'Roasted Chana',
                     'Cheese Balls', 'Ribbon Pakoda'], (20, 120)),
    'Sweets':      (['Gulab Jamun', 'Rasgulla', 'Mysore Pak', 'Kaju Katli', 'Laddu', 'Jalebi',
                     'Soan Papdi', 'Barfi', 'Peda', 'Halwa', 'Sandesh', 'Milk Cake'], (150, 600)),
    'Cold Drinks': (['Lemon Soda', 'Jaljeera', 'Buttermilk', 'Lassi', 'Rose Milk', 'Badam Milk',
                     'Mango Juice', 'Cola', 'Nimbu Pani', 'Kokum Sherbet', 'Iced Tea', 'Coconut Water',
                     'Aam Panna'], (25, 90)),
    'Hot Drinks':  (['Filter Coffee', 'Masala Chai', 'Ginger Tea', 'Green Tea', 'Hot Chocolate',
                     'Kahwa', 'Elaichi Tea', 'Tulsi Tea', 'Turmeric Latte', 'Black Coffee',
                     'Cardamom Coffee', 'Lemon Tea'], (15, 150)),
}
rows = []
for desc, (items, (lo, hi)) in catalogue.items():
    for it in items:
        rows.append((it, round(float(rng.uniform(lo, hi)) / 5) * 5, desc))
products = pd.DataFrame(rows, columns=['product_name', 'price', 'description'])
products.insert(0, 'product_id', range(1, len(products) + 1))

# ---- orders ------------------------------------------------------------
n_ord = 4000
never_cust = rng.choice(customers.customer_id, 6, replace=False)      # signed up, never bought
never_prod = rng.choice(products.product_id, 3, replace=False)        # listed, never sold
buyers = customers.customer_id[~customers.customer_id.isin(never_cust)].to_numpy()
sold = products.product_id[~products.product_id.isin(never_prod)].to_numpy()
w_c = rng.gamma(1.5, 1, len(buyers)); w_c /= w_c.sum()
w_p = rng.gamma(2.0, 1, len(sold)); w_p /= w_p.sum()
days = pd.date_range('2024-01-01', '2025-12-31', freq='D')
orders = pd.DataFrame({
    'customer_id': rng.choice(buyers, n_ord, p=w_c),
    'product_id': rng.choice(sold, n_ord, p=w_p),
    'order_date': rng.choice(days, n_ord).astype('datetime64[D]').astype(str),
}).sort_values('order_date', kind='stable').reset_index(drop=True)

# ---- write -------------------------------------------------------------
con = sqlite3.connect(DB)
con.executescript('''
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  email       TEXT NOT NULL UNIQUE,
  place       TEXT
);
CREATE TABLE products (
  product_id   INTEGER PRIMARY KEY,
  product_name TEXT NOT NULL,
  price        REAL NOT NULL,
  description  TEXT
);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id)
              ON DELETE RESTRICT ON UPDATE CASCADE,
  product_id  INTEGER NOT NULL REFERENCES products(product_id)
              ON DELETE RESTRICT ON UPDATE CASCADE,
  order_date  TEXT NOT NULL
);
''')
customers.to_sql('customers', con, if_exists='append', index=False)
products.to_sql('products', con, if_exists='append', index=False)
orders.to_sql('orders', con, if_exists='append', index=False)
con.commit()
for t in ['customers', 'products', 'orders']:
    print(t, con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
con.close()

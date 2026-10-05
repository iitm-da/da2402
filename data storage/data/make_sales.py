# Writes sales.csv and sales.parquet: 500 orders, 2023-2024.
# Same generator and seed as the Dash practice notebooks.
import numpy as np
import pandas as pd

np.random.seed(42)
dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
products = ['Laptop', 'Monitor', 'Keyboard', 'Mouse', 'Headphones']
regions = ['North', 'South', 'East', 'West']

rows = []
for _ in range(500):
    product = np.random.choice(products)
    region = np.random.choice(regions)
    category = 'Electronics' if product in ['Laptop', 'Monitor'] else 'Accessories'
    date = np.random.choice(dates)
    sales = np.random.randint(100, 5000)
    rows.append({'Date': date, 'Product': product, 'Region': region,
                 'Category': category, 'Sales': sales,
                 'Quantity': np.random.randint(1, 50)})

df = pd.DataFrame(rows)
df['Month'] = df['Date'].dt.to_period('M').astype(str)
df['Year'] = df['Date'].dt.year
for c in ['Product', 'Region', 'Category']:
    df[c] = df[c].astype('category')

df.to_csv('sales.csv', index=False)
df.to_parquet('sales.parquet', index=False)
print(df.shape)
print(df.dtypes)

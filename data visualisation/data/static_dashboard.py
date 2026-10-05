# Lecture 2: a static sales dashboard. No callbacks yet.
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

df = pd.read_parquet('sales.parquet')

monthly = df.groupby('Month')['Sales'].sum().reset_index()
by_region = df.groupby('Region', observed=True)['Sales'].sum().reset_index()

fig_month = px.line(monthly, x='Month', y='Sales', markers=True,
                    title='Sales by month')
fig_region = px.bar(by_region, x='Region', y='Sales', title='Sales by region')


def kpi(label, value):
    return dbc.Card(dbc.CardBody([html.P(label), html.H3(value)]))


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('Sales 2023-2024'), width=12)),
    dbc.Row([
        dbc.Col(kpi('Total sales', f"{df['Sales'].sum():,}"), width=3),
        dbc.Col(kpi('Orders', f"{len(df):,}"), width=3),
        dbc.Col(kpi('Units', f"{df['Quantity'].sum():,}"), width=3),
        dbc.Col(kpi('Average order', f"{df['Sales'].mean():,.0f}"), width=3),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_month), width=8),
        dbc.Col(dcc.Graph(figure=fig_region), width=4),
    ]),
])

if __name__ == '__main__':
    app.run(debug=True)

# Lecture 3: a static Gapminder dashboard. No callbacks.
import plotly.express as px
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

df = px.data.gapminder()
df07 = df[df['year'] == 2007]
# one colour per continent in every chart; px otherwise colours by order of appearance
COLORS = dict(zip(sorted(df['continent'].unique()), px.colors.qualitative.Plotly))

trend = df.groupby(['year', 'continent'])['lifeExp'].median().reset_index()
pop_t = df.groupby(['year', 'continent'])['pop'].sum().reset_index()

fig_anim = px.scatter(df, x='gdpPercap', y='lifeExp', size='pop', color='continent',
                      hover_name='country', animation_frame='year', animation_group='country',
                      log_x=True, size_max=55, range_x=[200, 150000], range_y=[20, 90],
                      color_discrete_map=COLORS,
                      title='GDP per capita and life expectancy, 1952-2007')
fig_line = px.line(trend, x='year', y='lifeExp', color='continent', markers=True,
                   color_discrete_map=COLORS,
                   title='Median life expectancy by continent')
fig_map = px.choropleth(df07, locations='iso_alpha', color='lifeExp', hover_name='country',
                        color_continuous_scale='Viridis', title='Life expectancy, 2007')
fig_tree = px.treemap(df07, path=[px.Constant('World'), 'continent', 'country'], values='pop',
                      color='lifeExp', color_continuous_scale='Viridis', title='Population, 2007')
fig_hist = px.histogram(df07, x='lifeExp', nbins=20, title='Life expectancy, 2007')
fig_box = px.box(df07, x='continent', y='lifeExp', points='all', hover_name='country',
                 title='Life expectancy by continent, 2007')
fig_area = px.area(pop_t, x='year', y='pop', color='continent', color_discrete_map=COLORS,
                   title='World population by continent')


def kpi(label, value):
    return dbc.Card(dbc.CardBody([html.P(label), html.H3(value)]))


def graph(fig, height=420):
    fig.update_layout(height=height, margin=dict(l=40, r=20, t=50, b=40))
    return dcc.Graph(figure=fig)


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('Gapminder, 1952-2007'), width=12)),
    dbc.Row([
        dbc.Col(kpi('Countries', f"{df['country'].nunique()}"), width=3),
        dbc.Col(kpi('Population, 2007', f"{df07['pop'].sum() / 1e9:.2f} bn"), width=3),
        dbc.Col(kpi('Median life expectancy, 2007', f"{df07['lifeExp'].median():.1f} years"), width=3),
        dbc.Col(kpi('Median GDP per capita, 2007', f"${df07['gdpPercap'].median():,.0f}"), width=3),
    ]),
    dbc.Row([
        dbc.Col(graph(fig_anim, 520), width=8),
        dbc.Col(graph(fig_line, 520), width=4),
    ]),
    dbc.Row([
        dbc.Col(graph(fig_map), width=6),
        dbc.Col(graph(fig_tree), width=6),
    ]),
    dbc.Row([
        dbc.Col(graph(fig_hist, 360), width=4),
        dbc.Col(graph(fig_box, 360), width=4),
        dbc.Col(graph(fig_area, 360), width=4),
    ]),
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)

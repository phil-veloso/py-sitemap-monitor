import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

import pandas as pd

#----------------------------------------------------------------------

import dbm
import config

#----------------------------------------------------------------------

conn 			= dbm.create_connection(config.DB_PATH)

table_sitemap 	= config.DOMAIN + '_sitemap'
table_url		= config.DOMAIN + '_url'

data_sitemap 	= pd.read_sql_query("SELECT * FROM {table}".format(table=table_sitemap), conn)
data_urls		= pd.read_sql_query("SELECT * FROM {table}".format(table=table_url), conn)

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

#----------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/sitemap':
         return dashboard_sitemap
    elif pathname == '/urls':
         return dashboard_urls
    else:
        return '404'

#----------------------------------------------------------------------

dashboard_sitemap = html.Div([
	html.H4(children='Sitemap'),
	dcc.Graph(
		id='life-exp-vs-gdp',
		figure={
			'data': [
				go.Scatter(
					x=df[df['continent'] == i]['gdp per capita'],
					y=df[df['continent'] == i]['life expectancy'],
					text=df[df['continent'] == i]['country'],
					mode='markers',
					opacity=0.7,
					marker={
						'size': 15,
						'line': {'width': 0.5, 'color': 'white'}
					},
					name=i
				) for i in df.continent.unique()
			],
			'layout': go.Layout(
				xaxis={'type': 'log', 'title': 'GDP Per Capita'},
				yaxis={'title': 'Life Expectancy'},
				margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
				legend={'x': 0, 'y': 1},
				hovermode='closest'
			)
		}
	)
])

dashboard_urls = html.Div([
	html.H4(children='Urls'),
	generate_table(data_urls)
])

#----------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)


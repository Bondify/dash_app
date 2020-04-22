# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 15:41:27 2020

@author: santi
"""
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import date, timedelta

app = dash.Dash()
server = app.server

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'example@remix.com': 'janejacobs'
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Import data
#https://raw.githubusercontent.com/Bondify/dash_app/master/worldmeter/info2020-04-21.csv

yesterday = date.today() - timedelta(days=1)
filename = 'https://raw.githubusercontent.com/Bondify/dash_app/master/worldmeter/info' + str(yesterday) + '.csv'

df = pd.read_csv(filename)
#df = pd.read_csv(r"C:\Users\santi\Google Drive\Master\Python\Web Scrapping\data\worldmeter\info2020-04-20.csv")

# Relative DF
df_relative = pd.DataFrame()

for c in df.country.unique():
    df_aux = df.loc[(df.total_cases>99)&(df.country==c),:].reset_index()
    df_aux['n_day'] = 0
    
    for i in range(0, len(df_aux)):
        df_aux.loc[i,'n_day'] = i
    
    df_relative = df_relative.append(df_aux)

df_relative['frame'] = df_relative['n_day']

last_day = df_relative.loc[df_relative.country=='S. Korea', 'n_day'].max()

df_relative = df_relative.loc[df_relative.n_day<=last_day,:]

# last = df_relative.loc[df_relative.country.isin(countries),:]
# rest = df_relative.loc[~df_relative.country.isin(countries),:]

# use_this = rest.append(last)

# fig = px.line(df_relative, x=df_relative['n_day'], y=df_relative['total_cases'], color='country', 
#                   height=700,
#                  template = 'simple_white',
#                  )
# dark_grey = '#787E81'
light_grey = 'rgb(204, 204, 204)'

traces = [
    go.Scatter(
        x = df_relative.loc[df_relative.country==c, 'n_day'],
        y = df_relative.loc[df_relative.country==c, 'total_cases'],
        mode='lines',
        legendgroup = c,
        name = c,
        customdata = df_relative.loc[df_relative.country==c, 'country'],
        line=dict(width=1, color = light_grey)) 
    for c in df_relative.country.unique()
        ]
                     
layout = go.Layout(showlegend=False, hovermode='closest', template='simple_white', height=700)
                     
fig = go.Figure(data=traces, layout=layout)
#fig.update_layout(showlegend=False)
fig.update_yaxes(type='log')

# for d in fig.data:
#     d.customdata = [d.name]
    
# dark_grey = '#787E81'
light_grey = 'rgb(204, 204, 204)'
    
col_options = [dict(label=x, value=x) for x in df_relative.sort_values(by='total_cases', ascending=False).country.unique()]

app.layout = html.Div(
    [
        html.H1("Demo: Plotly Express in Dash with Tips Dataset"),
   #     html.Label('Multi-Select Dropdown'),
        html.Div(
            [
                dcc.Dropdown(id = 'country-dropdown', options= col_options, value='Italy', multi=False),
                dcc.RadioItems(
                    id='crossfilter-yaxis-type',
                    options=[{'label': i.capitalize(), 'value': i} for i in ['linear', 'log']],
                    value='log',
                    labelStyle={'display': 'inline-block'}
            )
            ],
            style={"width": "15%", "float": "left"},
        ),
        html.Div([
        html.Pre(
            id = 'hover-data',
            )
        ]),
       dcc.Graph(id="graph", 
                 hoverData={'points': [{'customdata': 'Italy'}]},
                 style={"width": "75%", "display": "inline-block"}),
    ]
)

@app.callback(
        dash.dependencies.Output(component_id='graph', component_property='figure'),
        [dash.dependencies.Input('graph', 'hoverData'),
         dash.dependencies.Input(component_id='crossfilter-yaxis-type', component_property='value')]
        )

def create_figure(hover_data, y_axis_type):
    t = fig.data
    
    country_name = hover_data['points'][0]['customdata']
    
    last = [i for i in t if i.name == country_name]
    rest = [i for i in t if i.name != country_name]

    for i in last: i.line = dict(color='#13264B', dash='solid', width=4) 
    for i in rest: i.line = dict(color=light_grey, dash='solid', width=1)   
    

    fig.data = rest + last
    fig.update_yaxes(type=y_axis_type)

    return fig    

if __name__ == '__main__':
    app.run_server(debug=True)

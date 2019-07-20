import requests 
from datetime import datetime
import pandas as pd 
from pandas.io.json import json_normalize
import dash
import dash_table
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)

parks_resp = requests.get('http://mynpspass.herokuapp.com/api/parks/')
visits_resp = requests.get('http://mynpspass.herokuapp.com/api/visits')
parks = parks_resp.json()
all_visits = visits_resp.json()

park_visits = []
visits_by_state = {}
for park in parks:
  park_visits.append(len(park['visits']))

  if park['state'] not in visits_by_state:
    visits_by_state[park['state']] = len(park['visits'])
  else: 
    visits_by_state[park['state']] += len(park['visits'])

parks_overview_df = json_normalize(parks)
parks_overview_df['visits'] = park_visits

visits_by_state_nested = {'state': [], 'visits': []}
for state, visits in visits_by_state.items():
  visits_by_state_nested['state'].append(state)
  visits_by_state_nested['visits'].append(visits)

park_visits_df = pd.DataFrame(visits_by_state_nested)

visits_by_month = {}
visits_by_month_nested = {'month': [], 'visits': []}

for visit in all_visits:
  visit['date'] = datetime.strptime(visit['date'], '%Y-%m-%d')
  
  if visit['date'].month not in visits_by_month:
    visits_by_month[visit['date'].month] = 1
  else:
    visits_by_month[visit['date'].month] += 1

visits_by_month = sorted(visits_by_month.items())
visits_months_df = pd.DataFrame(visits_by_month, columns=['month', 'visits'])

app.layout = html.Div(children=[
  html.H1("Hi", id="title"),

   dcc.Graph(
     id='visits-by-state',
     figure={
       'data': [
        go.Choropleth(
          locations = park_visits_df['state'], 
          z = park_visits_df['visits'], 
          locationmode = 'USA-states', 
          colorscale = 'Greens',
          colorbar_title = "Park Visits")
       ],
       'layout': go.Layout(geo_scope='usa'),
     }
   ),

    dash_table.DataTable(
      id='interactive-park-visits-table',
      columns=[
        {"name": col, "id": col} for col in parks_overview_df.columns
      ],
      data=parks_overview_df.to_dict('records'),
      style_cell={'textAlign': 'left'},
      style_cell_conditional=[
        {'if': {'column_id': 'name'},
         'width': '40%'}
    ],
      style_table={
        'maxHeight': '18vw',
        'overflowY': 'scroll',
        'overflowX': 'scroll'
    },
      sort_action="native",
      sort_mode="multi"
    ),

    dcc.Graph(
      id='visits-by-month',
      figure={
        'data': [
          {'x': visits_months_df['month'], 'y': visits_months_df['visits'], 'type': 'bar'}
        ]
      }
    )
])

if __name__ == '__main__':
  app.run_server(debug=True)
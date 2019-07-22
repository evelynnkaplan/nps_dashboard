import requests 
from datetime import datetime
import pandas as pd 
from pandas.io.json import json_normalize
import dash
import dash_table
import dash_core_components as dcc 
import dash_html_components as html
import plotly.graph_objects as go

external_stylesheets = ['https://fonts.googleapis.com/css?family=Open+Sans|PT+Serif&display=swap']

app = dash.Dash(__name__,
external_stylesheets=external_stylesheets)

server = app.server

parks_resp = requests.get('http://mynpspass.herokuapp.com/api/parks/')
visits_resp = requests.get('http://mynpspass.herokuapp.com/api/visits')
passholders_resp = requests.get('http://mynpspass.herokuapp.com/api/passholders')
parks = parks_resp.json()
all_visits = visits_resp.json()
passholders = passholders_resp.json()

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

passholder_visits_by_year = {}
passholder_visits = []
for ph in passholders:
  full_name = f"{ph['first_name']} {ph['last_name']}"
  passholder_visits_by_year[full_name] = {}

  for visit in ph['visits']:
    passholder_visits.append(visit.split(', '))

for visit in passholder_visits:
  visit[2] = datetime.strptime(visit[2], '%Y-%m-%d').year
  
  if visit[2] not in passholder_visits_by_year[visit[0]]:
    passholder_visits_by_year[visit[0]][visit[2]] = 1
  else:
    passholder_visits_by_year[visit[0]][visit[2]] += 1

for ph in passholder_visits_by_year:
  lifetime_visits = 0
  years_visited = len(passholder_visits_by_year[ph])
  
  for visit_total in passholder_visits_by_year[ph].values():
    lifetime_visits += visit_total

  if years_visited != 0:
    passholder_visits_by_year[ph]['avg_visits'] = (lifetime_visits/years_visited)
  else:
    passholder_visits_by_year[ph]['avg_visits'] = 0

avg_visits = []

for ph in passholder_visits_by_year:
  avg_visits.append(passholder_visits_by_year[ph]['avg_visits'])

avg_visits_grouped = {
  'less than 1': 0, 
  '1-2': 0, 
  '2-3': 0, 
  '3-5': 0, 
  'More than 5': 0
}

for num in avg_visits:
  if num < 1:
    avg_visits_grouped['less than 1'] += 1
  elif 1 <= num < 2:
    avg_visits_grouped['1-2'] += 1
  elif 2 <= num < 3:
    avg_visits_grouped['2-3'] += 1
  elif 3 <= num <= 5:
    avg_visits_grouped['3-5'] += 1
  elif 5 < num:
    avg_visits_grouped['More than 5'] += 1

app.layout = html.Div(children=[
  html.H1("National Park Annual Passholder Data", id="title"),

  html.Div(id="visits-by-state-container", children=[
    html.H2("Park Visits by State", id="visits-by-state-title"),

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
  ]),
  
  html.Div(id="interactive-park-visits-container", children=[
    html.H2("Park Visits by National Park", id="interactive-park-visits-title"),

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
        'max-height': '500px',
        'overflowY': 'scroll',
        'overflowX': 'scroll'
    },
      sort_action="native",
      sort_mode="multi"
    ),
  ]),

  html.Div(id="visits-by-month-container", children=[
    html.H2("Park Visits by Month", id="visits-by-month-title"),

    dcc.Graph(
      id='visits-by-month',
      figure={
        'data': [
          {'x': visits_months_df['month'], 'y': visits_months_df['visits'], 'type': 'bar'}
        ]
      }
    ),
  ]),

  html.Div(id="avg-visits-per-year-container", children=[
    html.H2("Average Yearly Park Visits by Passholders", id="avg-visits-per-year-title"),

    dcc.Graph(
     id='avg-visits-per-year',
     figure={
       'data': [
        go.Pie(
          labels = list(avg_visits_grouped.keys()),
          values = list(avg_visits_grouped.values())
        )
       ],
     }
   ),
  ]),
])

if __name__ == '__main__':
  app.run_server(debug=True)
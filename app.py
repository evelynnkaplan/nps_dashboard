import requests 
import pandas as pd 
from pandas.io.json import json_normalize
import dash
import dash_table
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)

resp = requests.get('http://mynpspass.herokuapp.com/api/parks/')
parks = resp.json()
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

visits_df = pd.DataFrame(visits_by_state_nested)

# fig = px.bar(parks_overview_df, x='state', y='visits')

# fig1 = go.Figure(data=go.Choropleth(
#   locations=visits_df['state'], 
#   z = visits_df['visits'], 
#   locationmode = 'USA-states', 
#   colorscale = 'Greens',
#   colorbar_title = "Park Visits",
# ))

# fig1.update_layout(
#   geo_scope='usa'
# )

app.layout = html.Div(children=[
  html.H1("Hi"),

   dcc.Graph(
     id='visits-by-state',
     figure={
       'data': [
        go.Choropleth(
          locations=visits_df['state'], 
          z = visits_df['visits'], 
          locationmode = 'USA-states', 
          colorscale = 'Greens',
          colorbar_title = "Park Visits")
       ],
       'layout': go.Layout(geo_scope='usa'),
     }
   ),

  #  dcc.Graph(
  #    id = 'park-visits-table',
  #    figure = {
  #      'data': [
  #         go.Table(
  #           header=dict(values=list(parks_overview_df.columns),
  #             fill_color='paleturquoise',
  #             align='left'),
  #           cells=dict(values=[parks_overview_df.name, parks_overview_df.state, parks_overview_df.visits],
  #             fill_color='lavender',
  #             align='left')
  #             )
  #          ]}),

    dash_table.DataTable(
      id='interactive-park-visits-table',
      columns=[
        {"name": col, "id": col} for col in parks_overview_df.columns
      ],
      data=parks_overview_df.to_dict('records'),
      filter_action="native",
      sort_action="native",
      sort_mode="multi"
    )
])

if __name__ == '__main__':
  app.run_server(debug=True)
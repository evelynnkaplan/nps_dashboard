import requests 
import pandas as pd 
from pandas.io.json import json_normalize
import dash
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

# fig = px.bar(, x='state', y='visits')
# fig.show()

fig1 = go.Figure(data=go.Choropleth(
  locations=visits_df['state'], 
  z = visits_df['visits'], 
  locationmode = 'USA-states', 
  colorscale = 'Greens',
  colorbar_title = "Park Visits",
))

fig1.update_layout(
  geo_scope='usa'
)

fig1.show()

if __name__ == '__main__':
  app.run_server(debug=True)
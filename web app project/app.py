# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# loading required packages
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# read in datasets
vac_state = pd.read_csv("https://data.cdc.gov/api/views/unsk-b7fc/rows.csv?accessType=DOWNLOAD")
vac_county = pd.read_csv("https://data.cdc.gov/api/views/8xkx-amqh/rows.csv?accessType=DOWNLOAD")
trans = pd.read_csv("https://data.cdc.gov/api/views/8396-v7yb/rows.csv?accessType=DOWNLOAD")

# select required columns
vac_state = vac_state.loc[:, ['Date', 'Location', 'Administered_Dose1_Pop_Pct', 'Series_Complete_Pop_Pct']]
vac_state['Date'] = pd.to_datetime(vac_state['Date'])
vac_state.rename(columns={"Administered_Dose1_Pop_Pct": "At least 1 dose", "Series_Complete_Pop_Pct": "Fully vaccinated"}, inplace=True)

vac_county = vac_county.loc[:, ['Date', 'Recip_County', 'Recip_State', 'Series_Complete_Pop_Pct', 'Administered_Dose1_Pop_Pct']]
vac_county['Date'] = pd.to_datetime(vac_county['Date'])
vac_county.rename(columns={"Recip_County": "County", "Recip_State": "State", 
                          "Series_Complete_Pop_Pct": "Fully vaccinated rate", 
                          "Administered_Dose1_Pop_Pct": "At least one dose rate"}, inplace=True)
vac_county = vac_county[vac_county['State'] != 'UNK']

trans = trans.loc[:, ['state_name', 'county_name', 'report_date', 'cases_per_100K_7_day_count_change', 'percent_test_results_reported_positive_last_7_days']]
trans['report_date'] = pd.to_datetime(trans['report_date'])
trans.rename(columns={"state_name": "state", "county_name": "county", "report_date": "date", 
                      "cases_per_100K_7_day_count_change": "new_case", 
                      "percent_test_results_reported_positive_last_7_days": "pos_rate"}, inplace=True)
trans.loc[trans['new_case'] == 'suppressed', 'new_case'] = np.nan
trans.new_case = trans.new_case.str.replace(',', '').astype('float64')

# dictionary to states & counties
state_abv = np.sort(vac_county.State.unique().astype(str))
state_name = np.array(['Alaska', 'Alabama', 'Arkansas', 'American Samoa', 'Arizona', 'California', 'Colorado', 
                      'Connecticut', 'District of Columbia', 'Delaware', 'Florida', 'Federated States of Micronesia', 
                      'Georgia', 'Guam', 'Hawaii', 'Iowa', 'Idaho', 'Illinois', 'Indiana', 'Kansas', 'Kentucky', 
                      'Louisiana', 'Massachusetts', 'Maryland', 'Maine', 'Marshall Islands', 'Michigan', 'Minnesota', 
                      'Missouri', 'Northern Mariana Islands', 'Mississippi', 'Montana', 'North Carolina', 'North Dakota', 
                      'Nebraska', 'New Hampshire', 'New Jersey', 'New Mexico', 'Nevada', 'New York State', 'Ohio', 'Oklahoma', 
                      'Oregon', 'Pennsylvania', 'Puerto Rico', 'Palau', 'Rhode Island', 'South Carolina', 'South Dakota', 
                       'Tennessee', 'Texas', 'Utah', 'Virginia', 'Virgin Islands', 'Vermont', 'Washington', 'Wisconsin', 
                       'West Virginia', 'Wyoming'], dtype=object)
state_dic = []
for i in range(len(state_name)):
    sub_dic = {'label': state_name[i], 'value': state_abv[i]}
    state_dic.append(sub_dic)
dic_tf = {'Increasing': True, 'Decreasing': False}

def get_key(val):
    for dic_list in state_dic:
        for value in dic_list.values():
            if val == value:
                return list(dic_list.values())[0]

county_dic = {}
for states in trans.state.unique():
    new_dic = {states: list(trans.loc[trans['state']==states, 'county'].unique())}
    county_dic.update(new_dic)            

# dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='US COVID-19 DATA TRACKER', 
    style={'textAlign': 'center'}),

    html.Div(children='''
        An up to date web analysis tool for covid-19 data.
    ''', style={'textAlign': 'center'}),
    
    html.H2("Vaccination Percent in States of the US", style={'textAlign': 'center'}), 
    
    html.Div([ 
      dcc.RadioItems( 
        id='vac_group',
        options=[{'label': i, 'value': i} for i in ['Fully vaccinated', 'At least 1 dose']],
        value='Fully vaccinated',
        labelStyle={'display': 'inline-block'})], style={'textAlign': 'center'}),
        
    dcc.Graph(id='us-graph'),

    dcc.Slider(
        id='date-slider',
        min=vac_state['Date'].min().value,
        max=vac_state['Date'].max().value,
        value=pd.to_datetime('2021-06-01').value,
        step=8.64e+13
    ), 
    html.Div(id='date-output'), 
    
    html.Hr(),
    
    html.H2("Table of Vaccination Rate for Selected States", style={'textAlign': 'center'}), 
    
    dcc.Dropdown(
        id='state-dropdown',
        options=state_dic,
        value='IL', 
        clearable=False
    ), 
    
    html.Div(children='''
        Choose the sorting variable:
    ''', style={'textAlign': 'center'}), 
    
    html.Div([ 
        dcc.RadioItems( 
            id='sort',
            options=[{'label': 'County Name', 'value': 'County'}, 
            {'label': 'Fully vaccinated', 'value': 'Fully vaccinated rate'}, 
            {'label': 'At least 1 dose', 'value': 'At least one dose rate'}], 
            value='County',
            labelStyle={'display': 'inline-block'}), 
    
        dcc.RadioItems( 
           id='order',
           options=[{'label': i, 'value': i} for i in ['Increasing', 'Decreasing']],
           value='Increasing',
           labelStyle={'display': 'inline-block'})], style={'textAlign': 'center'}), 
        
    dcc.Graph(id='table'), 
    
    dcc.Slider(
        id='date-slider2',
        min=vac_county['Date'].min().value,
        max=vac_county['Date'].max().value,
        value=pd.to_datetime('2021-06-01').value,
        step=8.64e+13
    ), 
    html.Div(id='date-output2'), 
    
    html.H2("7 Day Moving Averages", style={'textAlign': 'center'}),  
    
    html.Div(children='''
        Use the dropdown to select county
    ''', style={'textAlign': 'center'}), 
    
    dcc.Dropdown(
        id='county-dropdown',
        clearable=False
    ), 
    
    html.H3(id='date-range', style={'textAlign': 'center'}), 
    
    html.Div(children='''
        Use the slider to select range of date
    ''', style={'textAlign': 'center'}), 
    
    dcc.RangeSlider(
        id='range-slider',
        min=trans['date'].min().value,
        max=trans['date'].max().value,
        step=8.64e+13,
        value=[pd.to_datetime('2021-10-01').value, pd.to_datetime('2021-11-01').value]
    ), 
    
    dcc.Graph(id='pos-pct'), 
    
    dcc.Graph(id='new-case')    
])

@app.callback(
    Output('county-dropdown', 'options'),
    Input('state-dropdown', 'value'))
def set_county(selected_state):
    return [{'label': i, 'value': i} for i in county_dic[get_key(selected_state)]]

@app.callback(
    Output('county-dropdown', 'value'),
    Input('county-dropdown', 'options'))
def set_county_value(available_county):
    return available_county[0]['value']

@app.callback(
    Output('us-graph', 'figure'), 
    Output('date-output', 'children'), 
    Output('table', 'figure'), 
    Output('date-output2', 'children'), 
    Output('date-range', 'children'), 
    Output('pos-pct', 'figure'), 
    Output('new-case', 'figure'), 
    Input('vac_group', 'value'), 
    Input('date-slider', 'value'), 
    Input('state-dropdown', 'value'), 
    Input('sort', 'value'), 
    Input('order', 'value'), 
    Input('date-slider2', 'value'), 
    Input('county-dropdown', 'value'), 
    Input('range-slider', 'value'))
def update_figure(selected_group, select_date, 
selected_state, sort_value, order, state_date, 
selected_county, date_range): 
  
    vac_state_day = vac_state.loc[vac_state['Date'] == pd.Timestamp(select_date), :]

    fig = px.choropleth(vac_state_day, locations='Location', locationmode="USA-states", 
                    color=selected_group, scope="usa")
    
    date = pd.Timestamp(select_date).strftime('%Y-%m-%d')
    text = 'Display data until ' + date
    
    vac_county_filter = vac_county.loc[(vac_county['Date']==pd.Timestamp(state_date)) & 
    (vac_county['State']==selected_state) & 
    (vac_county['County'] != 'Unknown County'), 
    ['County', 'Fully vaccinated rate', 'At least one dose rate']].sort_values(sort_value, ascending = dic_tf[order])

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=list(vac_county_filter.columns), 
        fill_color='paleturquoise', align='left'), 
        cells=dict(values=[vac_county_filter.County, vac_county_filter['Fully vaccinated rate'], 
        vac_county_filter['At least one dose rate']], 
        fill_color='lavender', align='left'))])
    
    date2 = pd.Timestamp(state_date).strftime('%Y-%m-%d')
    text2 = 'Display data until ' + date2
    
    trans_day = trans[(trans['state']==get_key(selected_state)) & (trans['county']==selected_county) & 
                  (trans['date']>=pd.Timestamp(date_range[0])) & (trans['date']<=pd.Timestamp(date_range[1]))]
                  
    fig3 = px.line(trans_day, x="date", y="pos_rate", title='Daily % Positivity - 7 Day Moving Average')
    
    fig4 = px.line(trans_day, x="date", y="new_case", title='Daily New Cases per 100k - 7 Day Moving Average')
    
    date_range1 = pd.Timestamp(date_range[0]).strftime('%Y-%m-%d')
    date_range2 = pd.Timestamp(date_range[1]).strftime('%Y-%m-%d')
    text3 = 'Display data from ' + date_range1 + ' to ' + date_range2
    
    return fig, text, fig2, text2, text3, fig3, fig4

if __name__ == '__main__':
    app.run_server(debug=True)

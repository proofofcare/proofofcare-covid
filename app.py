import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
import plotly.express as px

import numpy as np
import pandas as pd

daily_df = pd.read_csv('data/daily_cases.csv')
daily_df.rename(columns = {'COVID-19 Cases':'Total COVID-19 Cases'}, inplace = True)

df = pd.read_csv("http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Case_Details.csv")
df.rename(columns = {"Reported_Date":"Reported Date"}, inplace = True)
most_recent = df['Reported Date'].iloc[-1]


test_df = pd.read_csv('http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Lab_Information.csv')

## daily count of covid cases
covid_count = df.groupby(by = "Reported Date").count()
daily_covid_cases = covid_count.iloc[-1][0]

BC_active_cases = daily_df['Active Cases'].sum()

one_week_trend = covid_count.Sex.tail(7).sum()

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.title = "Proof of Care - Covid Dashboard"

covid_graph = go.Figure(go.Scatter(x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA))
covid_graph.update_layout(
    title ="Daily Covid Cases in BC",
    paper_bgcolor = 'white',
    plot_bgcolor ='white',


)

app.layout = html.Div([
    html.Div([
        html.H1("Proof of Care - B.C. COVID -19 update",)
    ]),
    html.Div(
        className ='boxes_container',
        children = [
            html.Div(
                className = "update_boxes",
                children = [
                    html.P('Data Updated up to: {}' .format(most_recent))
            ]),
            html.Div(
                className = 'update_boxes',
                children = [
                    html.P("Daily Case: {}" .format(daily_covid_cases ))
            ]),
            html.Div(
                className ='update_boxes',
                children = [
                    html.P("Cases, One Week Trend: {}" .format(one_week_trend))
            ]),
            html.Div(
                className = 'update_boxes',
                children = [
                    html.P('Number of Active Cases in BC: {}' .format(BC_active_cases))]),
    ]),
    dcc.Graph(
        className = "daily_cases",
        figure = covid_graph),
    ### for this I want active cases and total cases displayed as a radioitem
    dcc.RadioItems(
        className = 'radioitem_active_total',
        id = 'active_total_radioitem',
        options = [{'label':i, 'value':i} for i in ['Total COVID-19 Cases','Active Cases']],
        value = 'Active Cases'),
    dcc.Graph(
        className = 'active_total_cases',
        id = 'active_total_graph')
])

@app.callback(
    Output('active_total_graph', 'figure'),
    [Input('active_total_radioitem', 'value')])

def active_total_graph_render(activeortotal):
    filtered_df = daily_df[['Health Authority',activeortotal]]
    fig = px.pie(filtered_df, values = activeortotal, names = 'Health Authority', hole = .4)
    fig.update_layout(
        title = (activeortotal + ' for Health Authorities in BC')
    )
    return fig


if __name__ =='__main__':
    app.run_server(debug = True)





### end

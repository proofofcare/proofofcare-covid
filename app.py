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
server = app.server
app.title = "Proof of Care - Covid Dashboard"

covid_graph = go.Figure(go.Scatter(x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA,
    marker = dict(color='#01AEEF')))
covid_graph.update_layout(
    title ="Daily Covid Cases in BC",
    paper_bgcolor = 'white',
    plot_bgcolor ='white',
    xaxis = dict(
        title = "Time"),
    yaxis =dict(
        title = "New Cases")
)

z = df.groupby(by = ['Sex','Age_Group']).count()

age_sex_bar = go.Figure(data = [
    go.Bar(name = 'M', x = df.Age_Group.unique(), y = z.HA, marker = dict(color = '#3D9BE9')),
    go.Bar(name = 'F', x = df.Age_Group.unique(), y = z.HA, marker = dict(color = '#3FE3D1'))
    ])
age_sex_bar.update_layout(
    barmode='stack',
    title = 'Age and Sex Relationship for Covid Cases',
    paper_bgcolor = 'white',
    plot_bgcolor = 'white',
    xaxis = dict(
        title  = 'Age Group'),
    yaxis = dict(
        title = 'COVID Cases')
    )

app.layout = html.Div([
    html.Div([
        html.H1("Proof of Care - B.C. COVID -19 update", style = {
            'font-family':'fantasy'
        })
    ]),
    html.Div(
        className ='boxes_container',
        children = [
            html.Div(
                className = "update_boxes",
                children = [
                    html.P('Data Updated for: {}' .format(most_recent))
            ]),
            html.Div(
                className = 'update_boxes',
                children = [
                    html.P("Daily Case: {}" .format(daily_covid_cases ))
            ]),
            html.Div(
                className ='update_boxes',
                children = [
                    html.P("Cases for Past Week: {}" .format(one_week_trend))
            ]),
            html.Div(
                className = 'last_update_box',
                children = [
                    html.P('Number of Active Cases in BC: {}' .format(BC_active_cases))]),
    ], style = {'font-family':'Lucida Grande', 'font-weight':'bold',
        'font-size':18,'color':'#878787'}),
    html.Div(
        className = 'daily_cases_container',
        children = [
            dcc.Graph(
                className = "daily_cases",
                figure = covid_graph),
    ]),
    html.Div(
        className = "radioitem_container",
        children = [
            dcc.RadioItems(
                className = 'radioitem_active_total',
                id = 'active_total_radioitem',
                options = [{'label':i, 'value':i} for i in ['Active Cases', 'Total COVID-19 Cases']],
                value = 'Active Cases'),
        ]),
    html.Div(
        className = 'bot_graph_container',
        children = [
            html.Div(
                className = "active_total_container",
                children = [
                    dcc.Graph(
                        className = 'active_total_cases',
                        id = 'active_total_graph'),
                    ]),
            html.Div(
                className = "sex_age_container",
                children = [
                    dcc.Graph(
                        className = "sex_age",
                        figure = age_sex_bar
                        )
                    ]),
    ]),
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

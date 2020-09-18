import dash
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
import plotly.express as px
from arcgis import GIS


import numpy as np
import pandas as pd

gis = GIS();
item = gis.content.get("f7d1318260b14ac2b334e81e55ee5c9e#data");
flayer = item.layers[0];
daily_df = pd.DataFrame.spatial.from_layer(flayer);
daily_df.rename(columns = {'Cases':'Total Cases', 'ActiveCases':'Active Cases', 'HA_Name':'Health Authority'}, inplace = True)

df = pd.read_csv("http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Case_Details.csv")
df.rename(columns = {"Reported_Date":"Reported Date"}, inplace = True)
most_recent = df['Reported Date'].iloc[-1]

## daily count of covid cases
covid_count = df.groupby(by = "Reported Date").count()
daily_covid_cases = covid_count.iloc[-1][0]
BC_active_cases = daily_df['Active Cases'].sum()
one_week_trend = covid_count.Sex.tail(7).sum()

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server
app.title = "Proof of Care - Covid Dashboard"

covid_graph = go.Figure(
    go.Scatter(
        x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA, name = 'Daily Cases', opacity = .8,
            marker = dict(color='#01AEEF')))
covid_graph.add_trace(
    go.Scatter(
        x = pd.to_datetime(covid_count.index).sort_values(), y = covid_count.HA.rolling(7).mean(), name = '7 Day Average',
            opacity = 1, marker = dict(color = '#3D9BE9')))
covid_graph.update_layout(
    title ="Daily Covid Cases in BC",
    paper_bgcolor = 'white',
    plot_bgcolor ='white',
    xaxis = dict(
        title = "Time",
    ),
    yaxis =dict(
        title = "New Cases"),
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
                    html.P('Active Cases: {}' .format(BC_active_cases))]),
            html.Div(
                className = 'update_boxes',
                children = [
                    html.P("Daily Case: {}" .format(daily_covid_cases ))
            ]),
            html.Div(
                className = "update_boxes",
                children = [
                    html.P("Total Recovered: {}" .format(daily_df.Recovered.sum()))
                ]
            ),
            html.Div(
                className ='last_update_box',
                children = [
                    html.P("Cases for past 7 days: {}" .format(one_week_trend))
            ]),
    ], style = {'font-family':'Lucida Grande', 'font-weight':'bold',
        'font-size':18,'color':'#7d7d7d'}),
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
                options = [{'label':i, 'value':i} for i in ['Active Cases', 'Total Cases', 'Recovered']],
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
    html.Div([
        html.A('@Proof of Care Inc', href = 'https://www.proofofcare.com/'),
            html.Div([
                html.P("Sources from ", style = {'display':'inline'}),
                html.A("bccdc", href = "http://www.bccdc.ca/health-info/diseases-conditions/covid-19/data",
                style = {'display':'inline'})])
    ], style = {'margin-left':'5px', 'float':'right'})
])

@app.callback(
    Output('active_total_graph', 'figure'),
    [Input('active_total_radioitem', 'value')])

def active_total_graph_render(activeortotal):
    filtered_df = daily_df[['Health Authority',activeortotal]]
    fig = px.pie(filtered_df, values = activeortotal, names = 'Health Authority', hole = .4)
    fig.update_layout(
        title = (activeortotal + ' Region Distribution in BC')
    )
    return fig




if __name__ =='__main__':
    app.run_server(debug = True)





### end

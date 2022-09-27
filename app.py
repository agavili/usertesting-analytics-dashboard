from ctypes import alignment
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dash.dependencies import Output, Input




data = pd.read_csv('cleaned_data.csv')

comp_by_date = data.groupby(by=['date'])['comp'].sum().to_frame()
comp_by_date = comp_by_date.reset_index()

day_cats = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
num_test_weekday = data.groupby(['day_of_week']).count().drop(
    ['rating', 'device', 'date', 'time', 'comp','day_quarter'], axis=1).reset_index().groupby(['day_of_week']).sum().reindex(day_cats).reset_index()

tod = data['day_quarter'].value_counts().to_frame().reset_index().rename(columns={'index':'day_quarter', 'day_quarter':'count'})

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "UserTesting Analytics: Understand Your Side Hustle Income Flow!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="💻", className="header-emoji"),
                html.H1(
                    children="UserTesting Analytics", className="header-title"
                ),
                html.H2(
                    children="Understand Your Side Hustle Income Flow!\n", className="follower-header-title"
                ),
                html.P(
                    children="Get insights on revenue generated, test frequency, and optimal days and times for taking tests and making money",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Device type",
                                 className="menu-title"),
                        dcc.Dropdown(
                            id="device-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in np.sort(data.device.unique())
                            ],
                            value="All Devices",
                            clearable=True,
                            className="dropdown",
                            placeholder="All Devices"                        ),
                    ]

                ),

                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.date.min(),
                            max_date_allowed=data.date.max(),
                            start_date=data.date.min(),
                            end_date=data.date.max(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": comp_by_date["date"],
                                    "y": comp_by_date["comp"],
                                    "type": "lines",
                                    "hovertemplate": "$%{y:.2f}"
                                    "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Compensation During Test Period",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True,
                                'title': "Date"},
                                "yaxis": {
                                    "tickprefix": "$",
                                    "fixedrange": True,
                                    'title': "Compensation (Dollars)"
                                },
                                "colorway": ["#5C7E96"],
                            },
                        },
                    ),
                    className="card",
                ),

                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": num_test_weekday["day_of_week"],
                                    "y": num_test_weekday["ID"],
                                    "type": "bar",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Weekly Test Frequency",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True,'title': "Day of Week"},
                                "yaxis": {"fixedrange": True,'title': "Number of Tests"},
                                "colorway": ["#5C7E96"],
                            },
                        },
                    ),
                    className="card",
                ),

                html.Div(
                    children=dcc.Graph(
                        id="quarter-time-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    'values': tod['count'],
                                    'labels': ['Afternoon (2pm - 7pm)', 'Late Morning (10am - 1pm)', 'Night (7pm onward)', 'Morning (5am - 9am)'],
                                    'type': 'pie',
                                    'marker': {'colors':['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)', 'rgb(36, 55, 57)', 'rgb(6, 4, 4)']},
   
                                    # "hovertemplate": "%{y:.2f}"
                                    # "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Daily Test Frequency",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "tickprefix": "",
                                    "autorange": True,
                                },
                                # "colorway": ["#5C7E96"],
                            },
                        },
                    ),
                    className="card",
                ),                

            ],
            className="wrapper",
        ),
    ]
)


#CALLBACK 
@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure"), Output("quarter-time-chart", "figure") ],
    [
        Input("device-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(device, start_date, end_date):

    if device == None or device == 'All Devices':
        device_name = 'All Devices'
        mask = (
            (data.date >= start_date)
            & (data.date <= end_date)
        )
    else:
        device_name = device
        mask = (
            (data.device == device)
            & (data.date >= start_date)
            & (data.date <= end_date)
        )

    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data.groupby(by=['date'])['comp'].sum().to_frame().reset_index()["date"],
                "y": filtered_data.groupby(by=['date'])['comp'].sum().to_frame().reset_index()["comp"],
                "type": "lines",
                "hovertemplate": "%{x}, $%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Compensation During Test Period (" + device_name +")",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True,
                    'title': "Date"},
            "yaxis": {"tickprefix": "$", "fixedrange": True,'title': "Compensation (Dollars)"},
            "colorway": ["#5C7E96"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data.groupby(['day_of_week']).count().drop(
    ['rating', 'device', 'date', 'time', 'comp','day_quarter'], axis=1).reset_index().groupby(['day_of_week']).sum().reindex(day_cats).reset_index()["day_of_week"],
                "y": filtered_data.groupby(['day_of_week']).count().drop(
    ['rating', 'device', 'date', 'time', 'comp','day_quarter'], axis=1).reset_index().groupby(['day_of_week']).sum().reindex(day_cats).reset_index()["ID"],
                "type": "bar",
            },
        ],
        "layout": {
            "title": {
                "text": "Weekly Test Frequency (" + device_name +")",
                "x": 0.05,
                "xanchor": "left"
            },
            "xaxis": {"fixedrange": True, 'title': "Day of Week"},
            "yaxis": {"fixedrange": True, 'title': 'Number of Tests'},
            "colorway": ["#5C7E96"],
        },
    }

    tod_chart_figure = {
        "data": [
            {
            'values':filtered_data['day_quarter'].value_counts().to_frame().reset_index().rename(columns={'index':'day_quarter', 'day_quarter':'count'})['count'],
            'labels': ['Afternoon (2pm - 7pm)', 'Late Morning (10am - 1pm)', 'Night (7pm onward)', 'Morning (5am - 9am)'],
            'type': 'pie',
            'marker': {'colors':['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)', 'rgb(36, 55, 57)', 'rgb(6, 4, 4)']},
            
            },
        ],
        "layout": {
            "title": {
                "text": "Daily Test Frequency (" + device_name +")",
                "x": 0.05,
                "xanchor": "left"
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
        },   
    }
    return price_chart_figure, volume_chart_figure,tod_chart_figure






if __name__ == "__main__":
    app.run_server(debug=True)

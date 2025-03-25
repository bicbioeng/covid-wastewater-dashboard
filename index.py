import dash
from dash import html, dcc, Input, Output, State
import dash_daq as daq
import pandas as pd
import os
import numpy as np
import joblib
import pickle

# Initialize the Dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

# Load state population data
state_population_df = pd.read_csv("us-state-populations.csv")

# Load the saved models
rf_model = joblib.load('random_forest_model.pkl')
arima_model = pickle.load(open('arima_model.pkl', 'rb'))
sarima_model = pickle.load(open('sarima_model.pkl', 'rb'))

# Load the last day number from the text file (for Random Forest)
with open('last_data_info.txt', 'r') as f:
    lines = f.readlines()
    last_day_number = int(lines[0].split(': ')[1])

# List of U.S. states
us_states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
    'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
    'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
    'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina',
    'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]

# Visitor count file
visitor_count_file = 'visitor_count.txt'
if not os.path.exists(visitor_count_file):
    with open(visitor_count_file, 'w') as f:
        f.write('0')

def update_visitor_count():
    with open(visitor_count_file, 'r+') as f:
        count = int(f.read())
        count += 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    return count

def get_risk_level(value):
    if value <= 1.5:
        return "Very Low"
    elif 1.5 < value <= 3:
        return "Low"
    elif 3 < value <= 4.5:
        return "Moderate"
    elif 4.5 < value <= 8:
        return "High"
    else:  # value > 8
        return "Very High"

# Prediction Functions
def predict_rf_daily_deaths(viral_activity_level, days=5):
    if viral_activity_level == 0:
        return [0] * days  # Return zero deaths if viral activity is zero
    rf_input = np.array([[viral_activity_level, last_day_number + i + 1] for i in range(days)])
    rf_preds = rf_model.predict(rf_input)
    return rf_preds.tolist()  # Return as list for Dash compatibility

def predict_arima_daily_deaths(viral_activity_level, days=5):
    if viral_activity_level == 0:
        return [0] * days  # Return zero deaths if viral activity is zero
    exog_future = np.array([[viral_activity_level]] * days)
    arima_preds = arima_model.forecast(steps=days, exog=exog_future)
    return [abs(pred) for pred in arima_preds.tolist()]  # Ensure positive values

def predict_sarima_daily_deaths(viral_activity_level, days=5):
    if viral_activity_level == 0:
        return [0] * days  # Return zero deaths if viral activity is zero
    exog_future = np.array([[viral_activity_level]] * days)
    sarima_preds = sarima_model.forecast(steps=days, exog=exog_future)
    return [abs(pred) for pred in sarima_preds.tolist()]  # Ensure positive values

def predict_deaths_over_days(viral_activity, model_type):
    if model_type == 'Random Forest':
        return predict_rf_daily_deaths(viral_activity)
    elif model_type == 'ARIMA':
        return predict_arima_daily_deaths(viral_activity)
    elif model_type == 'SARIMA':
        return predict_sarima_daily_deaths(viral_activity)
    return [0] * 5  # Fallback

# Sample fun facts
fun_facts = [
    {
        "question": "Definition of Viral Activity",
        "answer": "The Wastewater Viral Activity Level is a calculated measure that allows us to aggregate wastewater sample data to get state/territorial, regional, and national levels and see trends over time. \n The value associated with the Wastewater Viral Activity Level is the number of standard deviations above the baseline, transformed to the linear scale. The formula is Wastewater Viral Activity Level = e ^ # of standard deviations relative to baseline."
    },
    {
        "question": "What is wastewater surveillance?",
        "answer": "Wastewater surveillance is an innovative public health tool that involves analyzing sewage to monitor the presence of viruses, bacteria, and other pathogens, such as the virus that causes COVID-19 (SARS-CoV-2). By collecting samples from wastewater treatment plants, scientists can detect traces of these pathogens shed by people through their waste, providing valuable insights into community health trends. This method serves as a broad, population-level screening system that complements traditional medical surveillance."
    },
    {
        "question": "How long can COVID-19 survive in wastewater?",
        "answer": "The genetic material (RNA) of SARS-CoV-2, the virus responsible for COVID-19, can remain detectable in wastewater for several days after being shed by infected individuals. While the virus itself is unlikely to remain infectious in sewage due to environmental factors like temperature, dilution, and treatment processes, its RNA fragments are stable enough to be identified through sensitive laboratory techniques, such as polymerase chain reaction (PCR) testing, for up to a week or more, depending on conditions."
    },
    {
        "question": "Why use wastewater for tracking?",
        "answer": "Wastewater tracking is a powerful tool because it can detect disease outbreaks early, often before individuals show symptoms or seek medical care. Known as an early warning system, it identifies the presence of pathogens in a community even when people are asymptomatic. Wastewater data can reveal changes in disease trends before they appear in clinical cases, giving health officials a head start to prepare healthcare providers and hospital systems for potential increases in visits and hospitalizations. This information also supports public health prevention efforts, such as targeted messaging or resource allocation."
    },
    {
        "question": "Wastewater monitoring provides early detection of increasing cases.",
        "answer": "One of the standout benefits of wastewater monitoring is its ability to provide early detection of rising infection rates within a community. Because people shed viruses like SARS-CoV-2 in their waste shortly after infection—often before symptoms develop—wastewater analysis can signal an uptick in cases days or even weeks before these trends are reflected in clinical data. This proactive approach allows public health officials to respond swiftly and effectively to emerging outbreaks."
    },
    {
        "question": "Wastewater monitoring is independent from medical systems.",
        "answer": "Unlike traditional health surveillance, which relies on people seeking medical care or getting tested, wastewater monitoring operates independently of healthcare systems. It can detect infections in a community regardless of whether individuals have symptoms, access to doctors, or available testing. This makes it an equitable and inclusive tool, capturing data from entire populations served by a sewer system, not just those interacting with medical services."
    },
    {
        "question": "Wastewater monitoring is fast and efficient.",
        "answer": "The process of wastewater monitoring is remarkably quick, taking only about five to seven days from the moment a toilet is flushed to when results are available. A single sample from a wastewater treatment plant can provide comprehensive data on disease trends for hundreds, thousands, or even millions of people, depending on the facility’s service area. This efficiency makes it a scalable and cost-effective method for tracking public health on a large scale."
    },
    {
        "question": "Wastewater monitoring has national coverage.",
        "answer": "Wastewater monitoring has been widely adopted across the United States, with programs implemented in all 50 states, 7 territories, and select tribal communities. Any community served by a municipal wastewater collection system can participate, making it a versatile tool for urban and rural areas alike. This broad coverage ensures that public health officials have a consistent, nationwide dataset to monitor and compare disease trends."
    },
    {
        "question": "Wastewater monitoring can be used to track emerging health threats.",
        "answer": "The flexibility of wastewater monitoring allows it to adapt to evolving public health challenges. Beyond tracking known diseases like COVID-19, it can be rapidly retooled to detect emerging threats, such as new viruses or pathogens. The Centers for Disease Control and Prevention (CDC) is exploring how this method can be expanded to address other infectious diseases, enhancing our ability to respond to future health crises."
    },
    {
        "question": "Wastewater monitoring can be used to track changes in health threats.",
        "answer": "By analyzing the genetic material of pathogens in wastewater—a field known as pathogen genomics—scientists can identify significant changes in these organisms, such as the emergence of new variants of SARS-CoV-2. This approach reveals where these changes are occurring, how widespread they are, and how they might impact public health. For instance, it has been used to track the prevalence of different COVID-19 variants in communities, offering critical insights into the virus’s evolution."
    },
    {
        "question": "Wastewater monitoring is complementary to other public health surveillance data.",
        "answer": "Wastewater data shines brightest when paired with other surveillance methods, such as clinical case reports or testing data. Together, these sources create a more complete and accurate picture of disease spread within a community. While wastewater monitoring provides a broad, population-level view, other data can offer specifics about individual cases, helping public health officials make informed decisions about interventions and resource distribution."
    },
    {
        "question": "Wastewater Viral Activity Categories",
        "answer": "Up to 1.5 – Very Low \n Greater than 1.5 and up to 3 – Low \n Greater than 3 and up to 4.5 – Moderate \n Greater than 4.5 and up to 8 – High \n Greater than 8 – Very High"
    }
]

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([], className="one-third column"),
        html.Div([
            html.H3("COVID Tracker: Learning from Wastewater", style={"margin-bottom": "0px", 'color': 'white', 'textAlign': 'center'}),
            html.H5("Analyze COVID trends via wastewater", style={"margin-top": "0px", 'color': 'white', 'textAlign': 'center'}),
        ], className="one-half column", id="title"),
        html.Div([
            html.H6(id='visitor_count', style={'color': 'orange', 'textAlign': 'center'}),
        ], className="one-third column", id='title1'),
    ], id="header", className="row flex-display", style={"margin-bottom": "5px"}),

    # Main content and fun facts side by side
    html.Div([
        # Tabs section
        html.Div([
            dcc.Tabs(id='tabs', children=[
                # Household Tab
                dcc.Tab(label='Viral Activity', children=[
                    html.Div([
                        html.Div([
                            html.Label("Enter Viral Activity Level:", style={'color': 'white', 'fontSize': 20, 'textAlign': 'center'}),
                            dcc.Input(id='household-number', type='number', value=0, min=0, step=0.1, style={'width': '200px', 'marginBottom': 10}),
                            html.Label("Select Model:", style={'color': 'white', 'fontSize': 20, 'textAlign': 'center'}),
                            dcc.Dropdown(
                                id='household-model',
                                options=[{'label': 'Random Forest', 'value': 'Random Forest'}, {'label': 'ARIMA', 'value': 'ARIMA'}, {'label': 'SARIMA', 'value': 'SARIMA'}],
                                value='Random Forest',
                                style={'width': '200px', 'marginBottom': 20}
                            ),
                            html.Div(id='household-result', style={'color': 'white', 'fontSize': 20, 'marginBottom': 20, 'textAlign': 'center'}),
                            html.Div(id='household-deaths', style={'color': 'white', 'fontSize': 20, 'marginBottom': 20, 'textAlign': 'center'}),
                        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                        html.Div([
                            html.Div([
                                daq.Gauge(
                                    id='household-gauge',
                                    label={'label': "COVID Risk Level", 'style': {'color': 'white'}},
                                    min=0,
                                    max=10,
                                    value=0,
                                    scale={
                                        'custom': {
                                            '0': 'Very Low',
                                            '1.5': 'Low',
                                            '3': 'Moderate',
                                            '4.5': 'High',
                                            '8': 'Very High'
                                        }
                                    },
                                    showCurrentValue=False,
                                    units="",
                                    color={"gradient": True, "ranges": {
                                        "blue": [0, 1.5], "green": [1.5, 3], "yellow": [3, 4.5], "orange": [4.5, 8], "red": [8, 10]
                                    }},
                                    size=200
                                ),
                                html.Div(id='household-risk-label', style={'color': 'white', 'fontSize': 16, 'textAlign': 'center', 'marginTop': '10px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            dcc.Graph(id='household-deaths-chart', style={'width': '350px', 'height': '300px', 'marginTop': '20px'})
                        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                    ], style={'padding': '20px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                ]),
                # State Tab
                dcc.Tab(label='State', children=[
                    html.Div([
                        html.Div([
                            html.Label("Select a US State:", style={'color': 'white', 'fontSize': 20, 'textAlign': 'center'}),
                            dcc.Dropdown(
                                id='state-dropdown',
                                options=[{'label': state, 'value': state} for state in us_states],
                                value='California',
                                style={'width': '300px', 'marginBottom': 10}
                            ),
                            html.Label("Viral Activity Level:", style={'color': 'white', 'fontSize': 20, 'textAlign': 'center'}),
                            dcc.Input(id='state-population', type='number', value=0, style={'width': '200px', 'marginBottom': 20}),
                            html.Label("Select Model:", style={'color': 'white', 'fontSize': 20, 'textAlign': 'center'}),
                            dcc.Dropdown(
                                id='state-model',
                                options=[{'label': 'Random Forest', 'value': 'Random Forest'}, {'label': 'ARIMA', 'value': 'ARIMA'}, {'label': 'SARIMA', 'value': 'SARIMA'}],
                                value='Random Forest',
                                style={'width': '200px', 'marginBottom': 20}
                            ),
                            html.Div(id='state-result', style={'color': 'white', 'fontSize': 20, 'marginBottom': 20, 'textAlign': 'center'}),
                            html.Div(id='state-deaths', style={'color': 'white', 'fontSize': 20, 'marginBottom': 20, 'textAlign': 'center'}),
                        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                        html.Div([
                            html.Div([
                                daq.Gauge(
                                    id='state-gauge',
                                    label="COVID Risk Level",
                                    min=0,
                                    max=10,
                                    value=0,
                                    scale={
                                        'custom': {
                                            '0': 'Very Low',
                                            '1.5': 'Low',
                                            '3': 'Moderate',
                                            '4.5': 'High',
                                            '8': 'Very High'
                                        }
                                    },
                                    showCurrentValue=False,
                                    units="",
                                    color={"gradient": True, "ranges": {
                                        "blue": [0, 1.5], "green": [1.5, 3], "yellow": [3, 4.5], "orange": [4.5, 8], "red": [8, 10]
                                    }},
                                    size=200
                                ),
                                html.Div(id='state-risk-label', style={'color': 'white', 'fontSize': 16, 'textAlign': 'center', 'marginTop': '10px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            dcc.Graph(id='state-deaths-chart', style={'width': '350px', 'height': '300px', 'marginTop': '20px'})
                        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                    ], style={'padding': '20px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                ])
            ])
        ], className="create_container seven columns"),

        html.Div([
            html.Div([
                html.H4("Wastewater Viral Activity Level", style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'}),
                html.P("Up to 1.5 – Very Low", style={'color': 'white', 'textAlign': 'center'}),
                html.P("Greater than 1.5 and up to 3 – Low", style={'color': 'white', 'textAlign': 'center'}),
                html.P("Greater than 3 and up to 4.5 – Moderate", style={'color': 'white', 'textAlign': 'center'}),
                html.P("Greater than 4.5 and up to 8 – High", style={'color': 'white', 'textAlign': 'center'}),
                html.P("Greater than 8 – Very High", style={'color': 'white', 'textAlign': 'center'}),
            ], style={'padding': '20px', 'marginBottom': '30px', 'backgroundColor': '#2a3b7a'}),
            # Fun Facts Carousel section
            html.Div([
                html.H4("Fun Facts", style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'}),
                html.Div(id='fun-fact-display', style={'color': 'white', 'textAlign': 'center'}),
                html.Div([
                    html.Button('Previous', id='prev-button', n_clicks=0, style={'marginRight': '10px', 'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'padding': '0px 10px 0px 10px'}),
                    html.Button('Next', id='next-button', n_clicks=0, style={'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'padding': '0px 10px 0px 10px'}),
                ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '20px'}),
                dcc.Interval(id='carousel-interval', interval=10000, n_intervals=0)
            ], style={'padding': '20px', 'marginBottom': '30px', 'backgroundColor': '#2a3b7a'}),

            # Explanation of Prediction Models
            html.Div([
                html.H4("How the Prediction Models Work", style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'}),
                
                html.Div([
                    html.H5("Random Forest", style={'color': '#4CAF50'}),
                    html.P("Random Forest is an ensemble learning method that constructs multiple decision trees and merges their outputs to improve prediction accuracy and reduce overfitting. It is widely used for both classification and regression tasks.", style={'color': 'white'}),
                ], style={'marginBottom': '20px'}),

                html.Div([
                    html.H5("ARIMA (AutoRegressive Integrated Moving Average)", style={'color': '#FF9800'}),
                    html.P("ARIMA is a time-series forecasting technique that combines autoregression (AR), differencing (I) to make the series stationary, and moving averages (MA). It is effective for linear patterns in time-series data.", style={'color': 'white'}),
                ], style={'marginBottom': '20px'}),

                html.Div([
                    html.H5("SARIMA (Seasonal ARIMA)", style={'color': '#FF5722'}),
                    html.P("SARIMA extends ARIMA by incorporating seasonal trends, making it useful for data with repeating seasonal patterns. It adds seasonal autoregressive, differencing, and moving average components to better model periodic fluctuations.", style={'color': 'white'}),
                ], style={'marginBottom': '20px'}),
            ], style={'padding': '20px', 'borderRadius': '10px', 'backgroundColor': '#2E2E2E'}),

            html.Div(
                [
                    html.H4("Important Links", style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'}),
                    html.Ul(
                        [
                            html.Li(
                                html.A(
                                    "South Dakota Trend, COVID-19",
                                    href="https://www.cdc.gov/nwss/rv/COVID19-statetrend.html?stateval=South%20Dakota",
                                    target="_blank",
                                    style={"text-decoration": "none", "color": "#007bff", "font-weight": "bold"},
                                )
                            ),
                            html.Li(
                                html.A(
                                    "State Trends, COVID-19",
                                    href="https://www.cdc.gov/nwss/rv/COVID19-statetrend.html?stateval=South%20Dakota",
                                    target="_blank",
                                    style={"text-decoration": "none", "color": "#007bff", "font-weight": "bold"},
                                )
                            ),
                            html.Li(
                                html.A(
                                    "COVID-19 Update for the United States",
                                    href="https://covid.cdc.gov/covid-data-tracker/#datatracker-home",
                                    target="_blank",
                                    style={"text-decoration": "none", "color": "#007bff", "font-weight": "bold"},
                                )
                            ),
                            html.Li(
                                html.A(
                                    "CDC NWSS About",
                                    href="https://www.cdc.gov/nwss/about.html?CDC_AA_refVal=https%3A%2F%2Fwww.cdc.gov%2Fnwss%2Fprogress.html",
                                    target="_blank",
                                    style={"text-decoration": "none", "color": "#007bff", "font-weight": "bold"},
                                )
                            ),
                            html.Li(
                                html.A(
                                    "CDC COVID-19 State Trend (Arizona)",
                                    href="https://www.cdc.gov/nwss/rv/COVID19-statetrend.html?stateval=Arizona",
                                    target="_blank",
                                    style={"text-decoration": "none", "color": "#007bff", "font-weight": "bold"},
                                )
                            ),
                            html.Li(
                                html.A(
                                    "Wastewater Surveillance Dashboard",
                                    href="https://wastewater.bicbioeng.org/page4",
                                    target="_blank",
                                    style={"text-decoration": "none", "color": "#007bff", "font-weight": "bold"},
                                )
                            )
                        ],
                        style={"list-style-type": "none", "padding": "0"},
                    ),
                ],
                style={'marginTop': '20px', 'padding': '20px', 'borderRadius': '10px', 'backgroundColor': '#2E2E2E'},
            )
        ], className="create_container five columns", style={'marginTop': '30px'}),
    ], className="row flex-display"),

], id="mainContainer", style={"display": "flex", "flex-direction": "column", "backgroundColor": "#1f2c56"})

# Callback for visitor count
@app.callback(
    Output('visitor_count', 'children'),
    [Input('visitor_count', 'id')]
)
def update_visitor_count_display(_):
    count = update_visitor_count()
    return f'Total Website Visits: {count}'

# Callback for Household tab
@app.callback(
    [Output('household-result', 'children'),
     Output('household-gauge', 'value'),
     Output('household-deaths', 'children'),
     Output('household-deaths-chart', 'figure'),
     Output('household-risk-label', 'children')],
    [Input('household-number', 'value'),
     Input('household-model', 'value')]
)
def update_household_output(number, model):
    if number is None:
        number = 0
    risk_level = get_risk_level(number)
    gauge_value = min(max(number, 0), 10)
    predicted_deaths = predict_deaths_over_days(number, model)
    
    result_text = f"Model: {model} | Viral Activity: {number} | Risk Level: {risk_level}"
    deaths_text = f"Predicted Deaths (Day 1): {int(predicted_deaths[0])}"
    
    fig = {
        'data': [{
            'x': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
            'y': [int(d) for d in predicted_deaths],
            'type': 'bar',
            'marker': {'color': 'orange'}
        }],
        'layout': {
            'title': {'text': 'Predicted Deaths Over 5 Days', 'font': {'color': 'white'}},
            'xaxis': {'title': 'Days', 'color': 'white', 'tickfont': {'color': 'white'}},
            'yaxis': {'title': 'Deaths', 'color': 'white', 'tickfont': {'color': 'white'}},
            'plot_bgcolor': '#1f2c56',
            'paper_bgcolor': '#1f2c56',
            'font': {'color': 'white'},
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40}
        }
    }
    
    return result_text, gauge_value, deaths_text, fig, f"Risk: {risk_level}"

# Callback for State tab - Update population
@app.callback(
    Output('state-population', 'value'),
    [Input('state-dropdown', 'value')]
)
def update_state_population(selected_state):
    if selected_state:
        population = state_population_df.loc[state_population_df['state'] == selected_state, 'pop_2014'].values
        return population[0]
    return 0

# Callback for State tab - Update result and chart
@app.callback(
    [Output('state-result', 'children'),
     Output('state-gauge', 'value'),
     Output('state-deaths', 'children'),
     Output('state-deaths-chart', 'figure'),
     Output('state-risk-label', 'children')],
    [Input('state-population', 'value'),
     Input('state-dropdown', 'value'),
     Input('state-model', 'value')]
)
def update_state_output(viral_activity, state, model):
    if viral_activity is None:
        viral_activity = 0
    risk_level = get_risk_level(viral_activity)
    gauge_value = min(max(viral_activity, 0), 10)
    predicted_deaths = predict_deaths_over_days(viral_activity, model)
    
    population = state_population_df.loc[state_population_df['state'] == state, 'pop_2014'].values[0] if state else 0
    result_text = f"State: {state} | Model: {model} | Population: {population:,} | Viral Activity: {viral_activity} | Risk Level: {risk_level}"
    deaths_text = f"Predicted Deaths (Day 1): {int(predicted_deaths[0])}"
    
    fig = {
        'data': [{
            'x': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
            'y': [int(d) for d in predicted_deaths],
            'type': 'bar',
            'marker': {'color': 'orange'}
        }],
        'layout': {
            'title': {'text': 'Predicted Deaths Over 5 Days', 'font': {'color': 'white'}},
            'xaxis': {'title': 'Days', 'color': 'white', 'tickfont': {'color': 'white'}},
            'yaxis': {'title': 'Deaths', 'color': 'white', 'tickfont': {'color': 'white'}},
            'plot_bgcolor': '#1f2c56',
            'paper_bgcolor': '#1f2c56',
            'font': {'color': 'white'},
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40}
        }
    }
    
    return result_text, gauge_value, deaths_text, fig, f"Risk: {risk_level}"

# Callback for Fun Facts Carousel (unchanged, omitted for brevity)
@app.callback(
    Output('fun-fact-display', 'children'),
    [Input('carousel-interval', 'n_intervals'),
     Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks')],
    [State('fun-fact-display', 'children')]
)
def update_fun_fact(n_intervals, prev_clicks, next_clicks, current_content):
    total_facts = len(fun_facts)
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    current_index = 0
    if current_content:
        for i, fact in enumerate(fun_facts):
            if fact["question"] in str(current_content):
                current_index = i
                break

    if triggered_id == 'prev-button':
        current_index = (current_index - 1) % total_facts
    elif triggered_id == 'next-button':
        current_index = (current_index + 1) % total_facts
    else:
        current_index = (n_intervals % total_facts)

    fact = fun_facts[current_index]
    
    # Split the answer by newline and intersperse with html.Br()
    answer_lines = fact["answer"].split('\n')
    answer_content = []
    for i, line in enumerate(answer_lines):
        answer_content.append(line.strip())  # Remove extra whitespace
        if i < len(answer_lines) - 1:  # Add <br> except after the last line
            answer_content.append(html.Br())

    return html.Div([
        html.P(fact["question"], style={'fontSize': 16, 'fontWeight': 'bold', 'marginBottom': '5px'}),
        html.P(answer_content, style={'fontSize': 14})
    ])

# Run the app
if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False, use_reloader=False, host="0.0.0.0")
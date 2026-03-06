# 🦠 COVID Tracker: Learning from Wastewater

An interactive web dashboard for analyzing COVID-19 trends using wastewater viral activity data. Users can input a wastewater viral activity level, select a U.S. state, and get predicted COVID-19 death estimates over the next 5 days using three different machine learning models.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Running Locally](#running-locally)
  - [Running with Docker](#running-with-docker)
- [Prediction Models](#prediction-models)
- [Viral Activity Level Scale](#viral-activity-level-scale)
- [Data Sources](#data-sources)
- [Links & References](#links--references)

---

## Overview

Wastewater surveillance is a powerful early-warning public health tool. Because people shed the SARS-CoV-2 virus in their waste before showing symptoms, wastewater data can signal rising infections days or weeks ahead of clinical reports. This dashboard translates raw wastewater viral activity levels into:

- A **COVID risk level** (Very Low → Very High)
- A **5-day predicted death forecast** using your choice of ML model
- State-level context with population data

---

## Features

- **Viral Activity Tab** – Enter any viral activity level and instantly see a color-coded risk gauge and a 5-day bar chart of predicted deaths.
- **State Tab** – Select a U.S. state to auto-populate its population and run state-level predictions.
- **Three Prediction Models** – Switch between Random Forest, ARIMA, and SARIMA to compare forecasts.
- **Educational Sidebar** – An auto-rotating carousel of facts about wastewater surveillance, plus explanations of each prediction model.
- **Visitor Counter** – Tracks total dashboard visits.
- **Dockerized** – Ready to deploy anywhere with a single command.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Dash](https://dash.plotly.com/) 2.11 |
| UI Components | Dash Bootstrap Components, Dash DAQ |
| Charting | Plotly 5.9 |
| ML Models | scikit-learn (Random Forest), statsmodels (ARIMA / SARIMA) |
| Data | pandas, NumPy |
| Containerization | Docker |
| Python | 3.10 |

---

## Project Structure

```
covid-wastewater-dashboard/
│
├── index.py                                  # Main Dash app — layout & callbacks
├── requirements.txt                          # Python dependencies
├── Dockerfile                                # Docker build config
│
├── assets/                                   # Static assets
│   ├── style.css / s1.css / styles.css       # Custom CSS
│   ├── tooltip.js                            # JS tooltip helper
│   └── logo.png / corona-logo-1.jpg         # Logos
│
├── # Trained ML Models
├── random_forest_model.pkl                   # Random Forest regressor
├── arima_model.pkl                           # ARIMA time-series model
├── sarima_model.pkl                          # SARIMA seasonal model
├── last_data_info.txt                        # Last training day number (for RF)
│
├── # Data Files
├── us-state-populations.csv                  # U.S. state population data
├── uscities.csv / uscounties.csv             # City & county reference data
├── population.csv                            # Population reference
├── time_series_covid19_confirmed_global.csv  # Global confirmed cases (JHU)
├── time_series_covid19_deaths_global.csv     # Global deaths (JHU)
├── time_series_covid19_recovered_global.csv  # Global recovered (JHU)
├── time_series_usa_states_waterwaste_*.csv   # Wastewater-derived state data
├── test_res.csv                              # Model test results
│
└── visitor_count.txt                         # Persistent visitor counter
```

---

## Getting Started

### Running Locally

**Prerequisites:** Python 3.10+

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd covid-wastewater-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
python index.py
```

Then open your browser to [http://localhost:8050](http://localhost:8050).

---

### Running with Docker

```bash
# Build the image
docker build -t covid-wastewater-dashboard .

# Run the container
docker run -p 8050:8050 covid-wastewater-dashboard
```

Then open your browser to [http://localhost:8050](http://localhost:8050).

---

## Prediction Models

### Random Forest
An ensemble learning method that builds multiple decision trees during training and averages their outputs. Takes the **viral activity level** and the **day number** as inputs to predict deaths. Well-suited for capturing non-linear relationships in the data.

### ARIMA (AutoRegressive Integrated Moving Average)
A classic time-series forecasting model. Uses past values and past forecast errors to predict future outcomes. The viral activity level is passed as an exogenous variable to guide the forecast.

### SARIMA (Seasonal ARIMA)
Extends ARIMA with seasonal components, making it better at capturing periodic fluctuations (e.g., weekly or monthly COVID wave patterns). Also uses viral activity as an exogenous variable.

All three models predict **daily deaths for the next 5 days** given a viral activity level.

---

## Viral Activity Level Scale

The Wastewater Viral Activity Level represents the number of standard deviations above baseline, transformed to a linear scale:

> **Wastewater Viral Activity Level = e^(standard deviations above baseline)**

| Activity Level | Risk Category |
|---|---|
| ≤ 1.5 | 🔵 Very Low |
| 1.5 – 3.0 | 🟢 Low |
| 3.0 – 4.5 | 🟡 Moderate |
| 4.5 – 8.0 | 🟠 High |
| > 8.0 | 🔴 Very High |

---

## Data Sources

- **JHU CSSE** – Global COVID-19 time series (confirmed, deaths, recovered)
- **CDC NWSS** – Wastewater viral activity data by U.S. state
- **U.S. Census** – State and city population figures

---

## Links & References

- [CDC NWSS – About Wastewater Surveillance](https://www.cdc.gov/nwss/about.html)
- [CDC COVID-19 Data Tracker](https://covid.cdc.gov/covid-data-tracker/#datatracker-home)
- [CDC NWSS – State Trends](https://www.cdc.gov/nwss/rv/COVID19-statetrend.html)
- [Wastewater Surveillance Dashboard (BIC Bioengineering)](https://wastewater.bicbioeng.org/page4)

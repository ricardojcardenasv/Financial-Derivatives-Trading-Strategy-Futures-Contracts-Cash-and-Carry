import requests as rq
# Makes a request to a web page, and prints the response text.

import pandas as pd
# Provides high-level data structures and functions designed to make working with structured or tabular data intuitive
# and flexible

from datetime import datetime as dt, timedelta as td
# Supplies classes for manipulating dates and times. datetime: A combination of a date and a time.
# timedelta: A duration expressing the difference between two date, time, or datetime instances.


import plotly.express as px

import streamlit as st





headers = {'Content-Type': 'application/json'}
# Sends the http json header to the browser to inform it what kind of data it expects.
params = (('currency', 'BTC'), ('expired', 'false'), ('kind', 'future'))
# Accepts a dictionary or tuples to send in the query string


response = rq.get('https://deribit.com/api/v2/public/get_instruments', headers=headers, params=params).json()
# The GET request method is used to request a resource from the server using the provided URL.


result = (response['result'])
# Accessing the value from the dictionary defined by the key "result"

monthlysp = [x for x in result if x['settlement_period'] == 'month' and
             any(char in x['instrument_name'] for char in ['MAR', 'JUN', 'SEP', 'DEC'])]
# Filter results to get the futures with a quarterly monthly settlement period.

results = pd.DataFrame(monthlysp)
# Create a two-dimensional tabular data structure with labeled axes (rows and columns).

resultsdc = results.loc[:, ['instrument_name', 'expiration_timestamp']]
# Drop unnecessary columns.

resultsdc['expiration_timestamp'] = pd.to_datetime(resultsdc['expiration_timestamp'], unit='ms')
# pd.to_datetime: This function converts to a pandas datetime object.


def extract_price_via_instrument(instrument_name):
    base_url = "https://deribit.com/api/v2/public/ticker"
    endpoint = f"{base_url}?instrument_name={instrument_name}"
    r = rq.get(endpoint).json()['result']
    last_price = r['last_price']
    index_price = r['index_price']
    return last_price, index_price
# Define the function extract_price_via_instrument, which takes an 'instrument_name' paramenter and uses the Deribit
# API to retrieve the last price and index price for the instrument.

def enrich(row):
    column_name = 'instrument_name'
    value = row[column_name]
    last_price, index_price = extract_price_via_instrument(value)
    row['last_price'] = last_price
    row['index_price'] = index_price
    return row
#Define the function enrich, which takes a row from a dataframe as input. It retrieves the value of the
# 'instrument_name' column for that row and calls the 'extract_price_via_instrument' function to get the last price
# and index price. It then adds these two values as new columns to the input row and returns the enriched row.

a= API_dataframe = resultsdc.apply(enrich, axis=1)
# Apply the 'enrich' function to every row in the dataframe 'resultsdc' using the 'apply' method and assign the result
# to a new dataframe called 'API_dataframe'. The 'axis=1' parameter indicates that the function should be applied to
# each row of the dataframe.

perc_basis = round((((API_dataframe['last_price'] - API_dataframe['index_price'])/API_dataframe['index_price'])*100),2)
# Calculation of the percentage basis of the futures contracts.

API_dataframe['percentage_basis'] = perc_basis
# Add a new column to the API_dataframe with the calculation of the percentage basis of the futures contracts.

gmt_time = dt.utcnow()
# get the current time in GMT

ann_perc_basis = round((perc_basis/(((API_dataframe['expiration_timestamp']) - gmt_time)/td(days=365))),2)
# Calculation of the annualized percentage basis of the futures contracts.

API_dataframe['a_percentage_basis'] = ann_perc_basis
# Add a new column to the API_dataframe with the calculation of the percentage basis of the futures contracts.

API_dataframe['Date'] = API_dataframe['expiration_timestamp'].dt.date


df_perc_basis = pd.DataFrame(API_dataframe, columns=['instrument_name', 'Date', 'percentage_basis'])


df_a_perc_basis = pd.DataFrame(API_dataframe, columns=['instrument_name', 'Date', 'a_percentage_basis'])


# Define a function to display the data as a plot
def display_plot(df):
    fig = px.line(df, x='instrument_name', y='percentage_basis',
               title='Bitcoin Futures Basis', markers=True,
               labels={ "instrument_name": "Instrument Name", "percentage_basis": "Percentage Basis (%)"})
    st.plotly_chart(fig)

# Define a function to display the data as a plot with annualized percentage basis
def display_a_plot(df):
    fig = px.line(df, x='instrument_name', y='a_percentage_basis',
               title='Bitcoin Futures Term Structure', markers=True,
               labels={ "instrument_name": "Instrument Name", "a_percentage_basis":
                   "Annualized Percentage Basis (%)"})
    st.plotly_chart(fig)

# Display the data as a plot
display_plot(df_perc_basis)

# Display the data as a plot with annualized percentage basis
display_a_plot(df_a_perc_basis)


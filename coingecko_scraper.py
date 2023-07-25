from bs4 import BeautifulSoup
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
import requests
from datetime import datetime, timedelta
import time
from collections import defaultdict
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
import csv


@dataclass
class Coin_info:
    value: float
    date: str
    time: str

'''
    initialize_soup(url, header)

    Creates, initializes a beautifulSoup object

    Parameters:
        url - target website url
        header - user agent header

    Returns:
        soup - initialized soup object
'''
def initialize_soup(url, header):
    soup = None

    try:
        html = requests.get(url, headers=header).text
        soup = BeautifulSoup(html, "lxml")

    except Exception as e:
        print("ERROR: Could not initialize soup object")
        print(e)

    return soup

'''
    get_coin_info(soup, coins, coin_dict)

    Scrapes a website for coin info and stores this data
    into a dictionary.

    Parameters:
        soup - BeautifulSoup object
        coins - list of coins to scrape data from
        coin_dict - dictionary to store data into

    Returns:
        coin_dict - populated dictionary
'''
def get_coin_info(soup, coins, coin_dict):
    section = soup.find_all("tr")

    for i in range(len(section)):
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = time.strftime("%H:%M:%S", time.localtime())
        coin_name = section[i].find(
            "span", class_="lg:tw-flex font-bold tw-items-center tw-justify-between"
        )
        coin_value = section[i].find("span", class_="no-wrap")

        if coin_name and coin_value and (coin_name.text.strip() in coins):
            # Parsing and storing coin info
            parsed_value = float(
                coin_value.text.replace("$", "").replace(",", "").strip()
            )
            coin_dict[coin_name.text.strip()].append(
                Coin_info(parsed_value, current_date, current_time)
            )

    return coin_dict

'''
    convert_to_list_of_dicts(coin_dict)

    Converts a dictionary into a list o dictionaries
    for later use when transfering this data onto a 
    csv file.

    Parameters:
        coin_dict - dictionary containing coin info

    Returns:
        result - a list of dictionaries
'''
def convert_to_list_of_dicts(coin_dict):
    result = []
    for coin_name, coin_info_list in coin_dict.items():
        for coin_info in coin_info_list:
            coin_data = {
                "coin_name": coin_name,
                "value": coin_info.value,
                "date": coin_info.date,
                "time": coin_info.time,
            }
            result.append(coin_data)
    return result

'''
    convert_to_list_of_dicts(coin_dict)

    Converts a dictionary into a list o dictionaries
    for later use when transfering this data onto a 
    csv file.

    Parameters:
        coin_dict - dictionary containing coin info
        coin - name of coin we want to query

    Returns:
        result - a list of dictionaries
'''
def convert_to_list_of_dicts(coin_dict, coin):
    result = []
    for coin_name, coin_info_list in coin_dict.items():
        if coin_name == coin:
            for coin_info in coin_info_list:
                coin_data = {
                    "coin_name": coin_name,
                    "value": coin_info.value,
                    "date": coin_info.date,
                    "time": coin_info.time,
                }
                result.append(coin_data)
    return result

'''
    dict_to_csv(coin_list_of_dicts)

    Populates a csv file with data from a dictionary

    Parameters:
        coin_list_of_dicts - list of dictionaries
        csv_name - name of csv
'''
def dict_to_csv(coin_list_of_dicts, csv_name):
    with open(csv_name, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["coin_name", "value", "date", "time"])
        writer.writeheader()
        writer.writerows(coin_list_of_dicts)

'''
    csv_to_dict(coin_dict)

    Populates a dictionary with data from a csv file

    Parameters:
        coin_dict - empty dictionary

    Returns:
        coin_dict - populated dictionary
'''
def csv_to_dict(coin_dict):
    coin_list_of_dicts = []
    with open("cache/data.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            coin_list_of_dicts.append(row)

    for coin_data in coin_list_of_dicts:
        coin_name = coin_data["coin_name"]
        value = coin_data["value"]
        date = coin_data["date"]
        time = coin_data["time"]

        if coin_name not in coin_dict:
            coin_dict[coin_name] = []

        # Make sure we don't insert duplicates in the dict values for a given key
        coin_info_arr = coin_dict[coin_name]
        flag = False
        for i in coin_info_arr:
            if i.date == date and i.time == time:
                flag = True
                break

        if not flag:
            coin_dict[coin_name].append(Coin_info(value, date, time))

    return coin_dict

'''
    csv_to_string()

    This displays the csv file we use for coin info storage

    Returns:
        csv_string - string representation of csv file
'''
def csv_to_string():
    csv_string = ''
    with open("cache/data.csv", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            csv_string += ', '.join(row) + '\n'

    return csv_string


'''
    scrape_data(soup, coins)

    This function scrapes and saves coin data onto a csv
    It is intended to be automated and run every couple
    minutes.

    Parameters:
        soup - BeautifulSoup object
        coins - list of coins to scrape data from
'''
def scrape_data(soup, coins):
    coin_dict = defaultdict(list)
    # Retrieve saved data in csv
    coin_dict = csv_to_dict(coin_dict)
    # Scrape data onto dictionary
    coin_dict = get_coin_info(soup, coins, coin_dict)
    # Convert dictionary to list of dictionaries
    coin_list_of_dicts = convert_to_list_of_dicts(coin_dict)
    # Save list of dictionaries data onto csv file
    dict_to_csv(coin_list_of_dicts, "cache/data.csv")

def graph_data(coin_name):

    coin_dict = defaultdict(list)
    # Retrieve saved data in csv
    coin_dict = csv_to_dict(coin_dict)
    coin_list_of_dicts = convert_to_list_of_dicts(coin_dict, coin_name)
    dict_to_csv(coin_list_of_dicts, "cache/graph_data.csv")

    # For reading from CSV file, use this instead:
    df = pd.read_csv("cache/graph_data.csv")

    fig = go.Figure()

    # Loop through each unique coin_name in the DataFrame and create a trace for it
    for coin_name in df['coin_name'].unique():
        coin_df = df[df['coin_name'] == coin_name]
        
        # Convert the date and time columns to a single datetime column
        coin_df['datetime'] = pd.to_datetime(coin_df['date'] + ' ' + coin_df['time'])
        
        fig.add_trace(
            go.Scatter(
                x=coin_df['datetime'],
                y=coin_df['value'],
                mode='lines',
                name=coin_name
            )
        )

    # Update layout to add titles and labels
    fig.update_layout(
        title='Cryptocurrency Values Over Time',
        xaxis_title='Date and Time',
        yaxis_title='Value',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1d', step='day', stepmode='backward'),
                    dict(count=7, label='1w', step='day', stepmode='backward'),
                    dict(count=1, label='1m', step='month', stepmode='backward'),
                    dict(count=6, label='6m', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1y', step='year', stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    return fig
from bs4 import BeautifulSoup
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
import requests
from datetime import datetime, timedelta
import time
from collections import defaultdict
import csv


@dataclass
class Coin_info:
    value: float
    date: str
    time: str


def initialize_soup(url, header):
    soup = None

    try:
        html = requests.get(url, headers=header).text
        soup = BeautifulSoup(html, "lxml")

    except Exception as e:
        print("ERROR: Could not initialize soup object")
        print(e)

    return soup


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


def dict_to_csv(coin_list_of_dicts):
    with open("../cache/data.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["coin_name", "value", "date", "time"])
        writer.writeheader()
        writer.writerows(coin_list_of_dicts)


def csv_to_dict(coin_dict):
    coin_list_of_dicts = []
    with open("../cache/data.csv", mode="r") as file:
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

        # Make sure we put duplicates in the dict values for a given key
        coin_info_arr = coin_dict[coin_name]
        flag = False
        for i in coin_info_arr:
            if i.date == date and i.time == time:
                flag = True
                break

        if not flag:
            coin_dict[coin_name].append(Coin_info(value, date, time))

    return coin_dict


"""
    scrape_data(soup, coins)

    This function scrapes and saves coin data onto a csv
    It is intended to be automated and run every couple
    minutes.

    Parameters:
        soup - BeautifulSoup object
        coins - list of coins to scrape data from
"""

def scrape_data(soup, coins):
    # Retrieve saved data in csv
    coin_dict = csv_to_dict(coin_dict)
    # Scrape data onto dictionary
    coin_dict = get_coin_info(soup, coins, coin_dict)
    # Convert dictionary to list of dictionaries
    coin_list_of_dicts = convert_to_list_of_dicts(coin_dict)
    # Save list of dictionaries data onto csv file
    dict_to_csv(coin_list_of_dicts)


def main():
    url = "https://www.coingecko.com"
    header = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    coins = ["Bitcoin", "Ethereum", "Tether", "Cardano", "Solana"]
    soup = initialize_soup(url, header)
    coin_dict = defaultdict(list)

    # Testing functionality:
    scrape_data(soup, coins)

    time.sleep(10)

main()

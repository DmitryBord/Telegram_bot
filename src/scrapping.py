from bs4 import BeautifulSoup
from requests import get
import time
import random
from typing import List, Dict
import pandas as pd


def parse(deal_type, rooms, max_price) -> None:
    # print("Please, wait...")
    flats: List = []
    pages: int = 1
    while pages <= 1:

        url: str = (
            f"https://www.cian.ru/cat.php?deal_type={deal_type}&engine_version=2&maxprice={max_price}&is_by_homeowner=1&offer_type=flat&p={pages}&region=1&room1={rooms}&type=4")
        response = get(url)
        html_soup = BeautifulSoup(response.text, "html.parser")
        flats_data1: List = html_soup.find_all("div", class_="_93444fe79c--card--ibP42 _93444fe79c--wide--gEKNN")
        flats_data2: List = html_soup.find_all("div", class_="_93444fe79c--card--ibP42")
        if flats_data1 or flats_data2:
            flats.extend(flats_data1)
            flats.extend(flats_data2)
            value = random.random()
            scaled_value = 1 + (value * (9 - 5))
            time.sleep(scaled_value)
        else:
            if pages == 1:
                print("Page is empty")
            break
        pages += 1
    found: bool = False
    data: Dict = {}
    for flat in flats:
        price: str = flat.find("span",
                               attrs={'data-mark': 'MainPrice'}).text

        link = flat.find("a", {"class": "_93444fe79c--media--9P6wN"}).get('href')
        my_price = f"{link}-{price}"
        key, value = my_price.split("-")
        data[key] = value
        found = True
    if not found:
        print("Sorry, there are no suitable apartments at this price")

    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_excel("apartments.xlsx")


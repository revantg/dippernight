import pickle
import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
import random

all_data = []


def scrape_rows(source_code):
    soup = BeautifulSoup(source_code)


def scrape_data(start_date, end_date):
    print("Starting for {} to {}".format(start_date, end_date))
    with open("area_info.pickle", "rb") as file:
        area_info = pickle.load(file)

    for area_name, area_id in area_info:
        print("Area Name {} || Area ID {}".format(area_name, area_id))
        for colliery in area_info[(area_name, area_id)]:
            url = "http://www.centralcoalfields.in/busns/RDOAPP/sodetails.php"
            params = {
                "sdt": start_date,
                "edt": end_date,
                "area": area_id,
                "colliery": colliery,
                "submit": "submit"
            }

            response = requests.request("POST", url, data=params)
            scrape_rows(response.text, area_id, area_name, colliery)

            save_in_pickle()

def scrape_rows(source_code, area_id, area_name, colliery_name):
    soup = BeautifulSoup(source_code)
    all_rows = soup.findAll('tr')[2].findAll('tr')[4].findAll('tr')
    global all_data
    temp_dict = {}
    for row in all_rows:
        if len(row.text.replace("*", "")) == 0:
            all_data.append(temp_dict)
            if 'SALE ORDER DATE' in temp_dict: temp_dict['SALE ORDER DATE'] = str_to_dt(temp_dict['SALE ORDER DATE'])
            if 'SALE ORDER EXPIRY DATE' in temp_dict : temp_dict['SALE ORDER EXPIRY DATE'] = str_to_dt(temp_dict['SALE ORDER EXPIRY DATE'])
            temp_dict = {
                'colliery_name' : colliery_name,
                'area_id' : area_name,
                'area_name' : area_id,
            }
        else:
            attribute, value = row.findAll('td')
            temp_dict[attribute.text.replace('.','')] = value.text

def scrape_yesterday():
    start_date = datetime.datetime.now() - datetime.timedelta(1)
    end_date = start_date

    str_start_date, str_end_date = get_str_date(start_date), get_str_date(end_date)
    scrape_data(str_start_date, str_end_date)

def str_to_dt(str_date):
    return datetime.datetime.strptime(str_date, "%Y-%m-%d")

def get_str_date(dt_obj):
    return datetime.datetime.strftime(dt_obj, "%Y-%m-%d")


def scrape_past_dates(start_date="2017-01-01", end_date="2019-01-07"):
    scrape_data(start_date, end_date)

def save_in_pickle():
    global all_data
    with open("scraped_data.pickle", "wb") as file:
        pickle.dump(all_data, file)

# scrape_yesterday()
scrape_past_dates()

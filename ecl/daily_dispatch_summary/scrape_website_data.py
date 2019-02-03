import pickle
import json
import datetime
import time
import time
import random
from bs4 import BeautifulSoup
import requests

all_data = []
scraped_consignees = []

def scrape_rows(source_code):
    global all_data

    soup = BeautifulSoup(source_code)
    table = soup.findAll('table')[2]

    rows = table.findAll('tr')
    headings = [i.text for i in rows[0].findAll('th')]

    for row in rows[1:]:
        temp = {}
        for i, element in enumerate(row.findAll('td')):
            temp[headings[i].replace('.', '')] = element.text
        all_data.append(process(temp))
        # break

def process(temp):
    if len(temp['SO DATE']) > 1:
        temp['SO DATE'] = str_to_dt(temp['SO DATE'])

    if len(temp['LOADING DATE']) > 1:
        temp['LOADING DATE'] = str_to_dt(temp['LOADING DATE'])
    
    return temp

def scrape_data(start_date, end_date):
    params = {
        'start_date' : start_date,
        'end_date' : end_date,
        'area' : 'all_areas',
        'coll' : 'all_coll',
        'submit' : ''
    }

    url = "http://112.133.239.50:8099/ecl_road_sale/report_truck_sales.php"
    r = requests.get(url, params = params)
    print(r.url)
    scrape_rows(r.content)

def str_to_dt(str_date):
    return datetime.datetime.strptime(str_date, "%d-%b-%y")


def str_to_dt2(str_date):
    return datetime.datetime.strptime(str_date, "%d-%b-%Y")


def get_str_date(dt_obj):
    return datetime.datetime.strftime(dt_obj, "%Y-%m-%d")


def save_in_pickle():
    global all_data
    with open("scraped_data.pickle", "wb") as file:
        pickle.dump(all_data, file)


def scrape_yesterday():
    start_date = datetime.datetime.now() - datetime.timedelta(1)
    end_date = start_date

    str_start_date, str_end_date = get_str_date(
        start_date), get_str_date(end_date)
    scrape_data(str_start_date, str_end_date)

def scrape_past_dates(start_date = "01-05-2018", end_date = "30-07-2018"):
    scrape_data(start_date, end_date)

scrape_past_dates()
print(len(all_data))
save_in_pickle()

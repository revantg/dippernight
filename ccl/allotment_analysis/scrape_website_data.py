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

def str_to_dt(str_date):
    return datetime.datetime.strptime(str_date, "%Y-%m-%d")

def get_str_date(dt_obj):
    return datetime.datetime.strftime(dt_obj, "%Y-%m-%d")

def save_in_pickle():
    global all_data
    with open("scraped_data.pickle", "wb") as file:
        pickle.dump(all_data, file)

def get_all_consignee_data():
    url = "http://www.centralcoalfields.in/busns/RDOAPP/allotment_analysis.php"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, features='lxml')

    options = soup.findAll('option')
    consignee_names = [option['value'] for option in options[1:]]

    for consignee_name in consignee_names:
        if consignee_name in scraped_consignees:
            print("skipping")
            continue
        print(consignee_name)
        params = {
            "sdt" : "2016-01-01",
            "edt" : "2019-01-07",
            "area" : consignee_name,
            "submit" : "submit",
        }

        response = requests.post(url, data = params)
        scrape_rows(response.text, consignee_name)
        scraped_consignees.append(consignee_name)
        add_consignee_name()

def add_consignee_name():
    with open("scraped_consignees.pickle", "wb") as file:
        pickle.dump(scraped_consignees, file)
    
def scrape_rows(source_code, consignee_name):
    global all_data

    soup = BeautifulSoup(source_code, features='lxml')
    if len(soup.findAll('table')[0].findAll('table')[1].findAll('tr')) == 0:
        return 
    
    rows = soup.findAll('table')[0].findAll('table')[1].findAll('tr')[1:-1]
    headings = [element.text for element in rows[0].findAll('td')]

    for row in rows[1:]:
        record = {
            'CONSIGNEE NAME' : consignee_name
        }
        for j, element in enumerate(row.findAll('td')):
            record[headings[j]] = element.text

        if 'ALLOTMENT DATE' in record:
            record['ALLOTMENT DATE'] = str_to_dt(record['ALLOTMENT DATE'])
        
        all_data.append(record)

    save_in_pickle()

with open("scraped_consignees.pickle", 'rb') as file:
    scraped_consignees = pickle.load(file)
with open("scraped_data.pickle", 'rb') as file:
    all_data = pickle.load(file)
get_all_consignee_data()


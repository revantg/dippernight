import pickle
import time
import datetime
import json
import os
from selenium import webdriver
import pymysql
from mongo_creds import *
from sshtunnel import SSHTunnelForwarder
import pymongo
from bs4 import BeautifulSoup

driver = webdriver.Firefox(
    executable_path=r'/home/revant/Downloads/geckodriver-v0.23.0-linux64/geckodriver')

url = "http://www.bcclweb.in/reports/deviation/deviation.php"

with open("log.txt", "a") as file:
    file.write("Executed at " +
               datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))

all_area_data = []

def scrape_all(start_date, end_date):
    global all_area_data

    start_date = get_date_string(start_date)
    end_date = get_date_string(end_date)

    desired_data = []

def fill_values():
    


def scrape_past_dates(start_date="2018-06-01", end_date="2019-01-01"):

    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    scrape_all(start_date_obj, end_date_obj)


def scrape_yesterday():
    start_date = datetime.datetime.now() - datetime.timedelta(1)
    end_date = start_date

    return scrape_all(start_date, end_date)


def get_date_string(date):
    format = "%Y-%m-%d"
    date_str = date.strftime(format)

    return date_str

def get_rows():
    colliery_data = []
    next_btn = driver.find_element_by_xpath("//*[@id = 'example_next']")

    while True:
        if 'disabled' in next_btn.get_attribute("class"):
            # page_data = scrape_rows()
            page_data = extract_with_bs4()
            colliery_data += page_data
            break

        # page_data = scrape_rows()
        page_data = extract_with_bs4()
        colliery_data += page_data

        btn = driver.find_element_by_xpath("//*[@id = 'example_next']/a")
        btn.click()
        time.sleep(2)
        next_btn = driver.find_element_by_xpath("//*[@id = 'example_next']")

    return colliery_data


def extract_with_bs4():
    source_code = driver.page_source
    soup = BeautifulSoup(source_code)

    rows = soup.findAll('tr')
    headings_row = rows[0]
    records_rows = rows[1:]

    headings = [heading.text for heading in headings_row.findAll('th')]

    data = []

    for record in records_rows:
        temp_dict = {}
        if len(record.findAll('td')) == 1:
            print("Found No Data")
            return data
        for index, cell in enumerate(record.findAll('td')):
            temp_dict[headings[index]] = cell.text
        data.append(temp_dict)
        # print(temp_dict)
        # break
    return data


def insert_data_mongo(data):

    print('\n\n\nLength of data', len(data), '\n\n\n\n')

    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_password=MONGO_PASS,
        remote_bind_address=('127.0.0.1', 27017)
    )
    print(server)
    server.start()

    client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
    db = client[MONGO_DB]

    print(db.collection_names())

    coll = db['loading_schedules']

    server.stop()

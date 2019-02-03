import pickle
import requests
import time
import datetime
import json
import os
import random
from selenium import webdriver
import pymysql
# from mongo_creds import *
from sshtunnel import SSHTunnelForwarder
import pymongo
from bs4 import BeautifulSoup

url = "http://www.bcclweb.in/reports/sales_order_details.php"

all_area_data = []

def scrape_data(start_date, end_date):
    global all_area_data

    with open("area_info.pickle", "rb") as file:
        area_info = pickle.load(file)

    # with open("scraped_data.pickle", "rb") as file:
    #     all_area_data = pickle.load(file)

    desired_data = []
    for area in list(area_info.keys())[:4]:
        area_id = area_info[area]['id']
        area_name = area
        collieries = area_info[area]['colliery_names']

        for (colliery_name, colliery_id) in collieries:
            params = {
                "area_id" : area_id,
                "colliery_id" : colliery_id,
                "start_date" : start_date,
                "end_date" : end_date,
                "submit" : ""
            }
            print("Scraping for Colliery {} ({}) in {} ({})".format(colliery_name, colliery_id, area_name, area_id))
            r = requests.post(url, data = params)

            scrape_rows(r.content, area_id, colliery_id, area_name, colliery_name)

            save_in_pickle()
            
def scrape_rows(source_code, area_id, colliery_id, area_name, colliery_name):
    global all_area_data

    soup = BeautifulSoup(source_code)
    rows = soup.findAll('tr')
    headings = [i.text for i in rows[0].findAll('th')]
    for row in rows[1:]:
        temp = {
            "area_id" : area_id,
            "colliery_id" : colliery_id,
            "area_name" : area_name,
            "colliery_name" : colliery_name
        }

        for i, data in enumerate(row.findAll('td')):
            temp[headings[i].replace('.', '')] = data.text    
        temp = process(temp)
        print(temp)
        all_area_data.append(temp)

def process(temp):
    if 'Sales Order Date' in temp:
        temp['Sales Order Date'] = str_to_dt(temp['Sales Order Date'])
    
    if 'Sales Order Expiry Date' in temp:
        temp['Sales Order Expiry Date'] = str_to_dt(temp['Sales Order Expiry Date'])

    return temp



def str_to_dt(str_date):
    return datetime.datetime.strptime(str_date, "%d-%m-%Y")


def dt_to_str(dt_obj):
    return datetime.datetime.strftime(dt_obj, "%Y-%m-%d")


def save_in_pickle():
    global all_area_data
    with open("scraped_data.pickle", "wb") as file:
        pickle.dump(all_area_data, file)


def scrape_yesterday():
    start_date = datetime.datetime.now() - datetime.timedelta(1)
    end_date = start_date

    str_start_date, str_end_date = dt_to_str(
        start_date), dt_to_str(end_date)

    scrape_data(str_start_date, str_end_date)


def scrape_past_dates(start_date="10-01-2019", end_date="19-01-2019"):
    scrape_data(start_date, end_date)

scrape_past_dates()

import pickle
import json
import datetime
import time
import time
import random
from bs4 import BeautifulSoup
import requests

all_data = []
def scrape_sales_num(sales_num):
    params = {
        'so_no' : sales_num, 
        'submit' : "submit"
    }
    url = "http://www.centralcoalfields.in/busns/RDOAPP/dispatch_detail_against_so.php"

    response = requests.post(url, data = params)
    
    scrape_rows(response.text, sales_num)
    print(len(all_data))
    save_in_pickle()

def scrape_rows(source_code, sales_num):
    soup = BeautifulSoup(source_code)
    # all_rows = soup.findAll('tr')[2].findAll('tr')[4].findAll('tr')
    all_rows = soup.findAll('tr')[2].findAll('tr')[2].findAll('tr')
    global all_data
    temp_dict = {}
    for row in all_rows:
        if len(row.text.replace("*", "")) == 0:
            if 'LIFTING DATE' in temp_dict: temp_dict['LIFTING DATE'] = str_to_dt(temp_dict['LIFTING DATE'])
            if len(temp_dict.keys()):
                all_data.append(temp_dict)
            temp_dict = {
                'SALES ORDER NO' : sales_num
            }
        else:
            attribute, value = row.findAll('td')
            temp_dict[attribute.text.replace('.','')] = value.text

def str_to_dt(str_date):
    return datetime.datetime.strptime(str_date, "%Y-%m-%d")

def get_str_date(dt_obj):
    return datetime.datetime.strftime(dt_obj, "%Y-%m-%d")

def scrape_sales_nums():
    with open("sales_order_details_data.pickle", "rb") as file:
        records = pickle.load(file)
    print(len(records))
    k = 0
    for record in records[600:]:
        k+=1
        if k%5==0:print("Currently at",k)
        if len(record.keys()):
            sales_order_num = record['SALE ORDER NO']
            if search(sales_order_num) == 0:
                scrape_sales_num(sales_order_num)
            else:
                print("Skipping")

def search(sales_order_num):
    global status
    try:
        if status[sales_order_num]:
            return 1
    except:
        return 0

def save_in_pickle():
    global all_data
    with open("scraped_data.pickle", "wb") as file:
        pickle.dump(all_data, file)



with open("scraped_data.pickle", "rb") as file:
    all_data = pickle.load(file)
status = {}
for i in all_data:
    status[i['SALES ORDER NO']] = 1
scrape_sales_nums()

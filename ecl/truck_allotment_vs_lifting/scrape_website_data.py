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


# def scrape_rows(source_code):
#     global all_data

#     soup = BeautifulSoup(source_code)
#     table = soup.findAll('table')[2]

#     rows = table.findAll('tr')
#     headings = [i.text for i in rows[0].findAll('th')]

#     for row in rows[1:]:
#         temp = {}
#         for i, element in enumerate(row.findAll('td')):
#             temp[headings[i].replace('.', '')] = element.text
#         all_data.append(process(temp))
#         # break


def scrape_data(start_date, end_date):

    with open("area_info.pickle", "rb") as file:
        area_info = pickle.load(file)

    for consignee_id in area_info:
        so_nums = area_info[consignee_id]['so_nums']
        consignee_name = area_info[consignee_id]['consignee_name']

        for so_num in so_nums:
            if search(so_num) == 1:
                print("skipping {} of {}".format(so_num, consignee_name))
                continue
            print("Scraping for {} of {}".format(so_num, consignee_name))
            scrape_consignee(so_num, consignee_id, consignee_name, start_date, end_date)
            save_in_pickle()

def scrape_consignee(so_num, consignee_id, consignee_name, start_date, end_date):
    params = {
        'start_date' : start_date,
        'end_date' : end_date,
        'consignee_code' : consignee_id,
        'so_no' : so_num,
        'submit' : ''
    }

    url = "http://112.133.239.50:8099/ecl_road_sale/deviation.php"
    r = requests.post(url, data = params)
    
    scrape_rows(r.text, so_num, consignee_id, consignee_name)


def scrape_rows(source_code, so_num, consignee_id, consignee_name):
    soup = BeautifulSoup(source_code)
    global all_data

    rows = soup.findAll('tr')
    headings = [i.text for i in rows[0].findAll('th')]

    for row in rows[1:]:
        temp = {
            'so_num' : so_num,
            'consignee_id' : consignee_id,
            'consignee_name' : consignee_name,
        }
        for i, element in enumerate(row.findAll('td')):
            temp[headings[i].replace('.','')] = element.text

        temp = process(temp)
        all_data.append(temp)

def process(temp):
    if 'ALLOTMENT DATE' in temp:
        temp['ALLOTMENT DATE'] = str_to_dt(temp['ALLOTMENT DATE'])
    return temp

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


def scrape_past_dates(start_date="01-01-2018", end_date="09-01-2019"):
    scrape_data(start_date, end_date)


def search(so_num):
    try :
        if scraped_so_nums[so_num]:
            return 1
    except:
        return 0

scraped_so_nums = {}
with open("scraped_data.pickle", "rb") as file:
    all_data = pickle.load(file)

for i in all_data:
    scraped_so_nums[i['so_num']] = 1

scrape_past_dates()
print(len(all_data))
save_in_pickle()

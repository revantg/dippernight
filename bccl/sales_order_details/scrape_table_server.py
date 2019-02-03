"""

    This program scrapes the data from BCCL website.
    It makes use of the area_info.pickle file generated by
    running the scraping.py prorgam.

    It saves the final Data in the pickle format in the file
    "scraped_data.pickle" and in JSON format in file
    "scraped_data.json".

    See usage at the end of the program.
    
"""

import pickle
import requests
import time
import datetime
import json
import os
import random
from selenium import webdriver
import pymysql
from mongo_creds import *
from sshtunnel import SSHTunnelForwarder
import pymongo
from bs4 import BeautifulSoup
# from creds import *
# from sql_operations import *

# path = r'/home/ubuntu/scraping2/sales_order_details'
# os.chdir(path)

# service = webdriver.chrome.service.Service('./chromedriver')
# service = webdriver.chrome.service.Service('./chromedriver')

# service.start()
# options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options = options.to_capabilities()
# driver = webdriver.Remote(service.service_url, options)

# driver = webdriver.Firefox(
#     executable_path=r'/home/revant/Downloads/geckodriver-v0.23.0-linux64/geckodriver')

url = "http://www.bcclweb.in/reports/sales_order_details.php"

all_area_data = []

with open("log.txt", "a") as file:
    file.write("Executed at " +
               datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))

# conn = pymysql.connect(
#     rds_host,
#     user=master_username,
#     passwd=master_password,
#     db=db_name,
#     connect_timeout=5)

"""
    This function is used for getting all the stored names and ids from area_info.pickle of all the
    areas and their collieries.
    It calls submit_values(area_id, area_name, colliery_id, colliery_name, start_date, end_date)
        for all the collieries and specified start_date and end_date.
        submit_values() selects Area, Colliery, Starting Date and Ending Date on the webpage and 
        then clicks the submit button.

    It then calls scrape_entry_pages()
        scrape_entry_pages() clicks on the next button on the displayed data.
        scrape_entry_pages() calls scrape_rows()
            scrape_rows() extracts data of the rows in the table.

    All the data is then appended to all_area_data

    Arguments:
        start_date : Starting Date
        end_date   : Ending Date

    All the arguments are automatically passed from scrape_yesterday() and scrape_past_dates()
"""


def scrape_all(start_date, end_date):
    global all_area_data

    with open("area_info.pickle", "rb") as file:
        area_info = pickle.load(file)

    with open("scraped_data.pickle", "rb") as file:
        all_area_data = pickle.load(file)

    start_date = get_date_string(start_date)
    end_date = get_date_string(end_date)

    desired_data = []
    for area in list(area_info.keys())[3:5]:
        area_id = area_info[area]['id']
        area_name = area
        collieries = area_info[area]['colliery_names']

        for (colliery_name, colliery_id) in collieries:
            try:
                print("getting the url")
                driver.get(url)
                print("got the url")
            except:
                pass

            """
                Select the respective Area, Colliery, Start_date and End_Date
                and click Submit button
            """
            success = submit_values(
                area_id, area_name, colliery_id, colliery_name, start_date, end_date)
            print(success)
            if not success:
                continue

            start_time = time.time()
            success = 1
            while success:
                # print("inside scrape_all")
                end_time = time.time()
                if end_time - start_time > 30:
                    success = 0
                    break
                try:
                    next_btn = driver.find_element_by_xpath(
                        "//*[@id = 'example_next']")
                    break
                except:
                    pass
            if not success:
                continue

            temp_dict = {
                'colliery_name': colliery_name,
                'colliery_id': colliery_id,
                'area_name': area_name,
                'area_id': area_id,
                # 'colliery_data' : colliery_data,
            }
            colliery_data = scrape_entry_pages()

            for record in colliery_data:
                record_json = temp_dict.copy()

                for attribute in record.keys():
                    record_json[attribute.replace('.', '')] = record[attribute]

                desired_data.append(record_json)
                print(record_json)
            print("Length :", len(desired_data))
            all_area_data.append(temp_dict)

            # if len(colliery_data):
            #     insert_data(conn, temp_dict)

        # Saves the data after scraping every Area
        with open("scraped_data.pickle", "wb") as file:
            pickle.dump(all_area_data, file)

    return desired_data


def scrape_all2(start_date, end_date):
    global all_area_data

    with open("area_info.pickle", "rb") as file:
        area_info = pickle.load(file)

    with open("scraped_data.pickle", "rb") as file:
        all_area_data = pickle.load(file)

    start_date = get_date_string(start_date)
    end_date = get_date_string(end_date)

    desired_data = []
    for area in list(area_info.keys())[3:5]:
        area_id = area_info[area]['id']
        area_name = area
        collieries = area_info[area]['colliery_names']

        for (colliery_name, colliery_id) in collieries:
            print("scraping for {} in area {}".format(colliery_name, area_name))
            data = submit_values2(area_id, area_name, colliery_id, colliery_name, start_date, end_date)
            print(data)


def submit_values2(area_id, area_name, colliery_id, colliery_name, start_date, end_date):
    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"area_id\"\r\n\r\n{area_id}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"colliery_id\"\r\n\r\n{colliery_id}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"start_date\"\r\n\r\n{start_date}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"end_date\"\r\n\r\n{end_date}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"submit\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--".format(
        area_id=area_id, colliery_id=colliery_id, start_date=start_date, end_date=end_date)
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'Postman-Token': "20ee4f0c-1060-46fe-80e7-dcbc028e98a5"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    return extract_with_bs4(response.text)


"""
    Select the respective Area, Colliery, Start_date and End_Date
    and click Submit button

    Arguments :
        area_id : ID of the area
        area_name : Name of the area
        colliery_id : ID of the colliery
        colliery_name : Name of the colliery
        start_date : Starting Date
        end_date : Ending Date

    This function is called from scrape_all function.
    All the arguments are called from scrape_all()
"""


def submit_values(area_id, area_name, colliery_id, colliery_name, start_date, end_date):

    try:
        print("getting the area")
        area = driver.find_element_by_xpath(
            "//*[@id = 'area_id'][1]//*[@value={}]".format(area_id))
        print(area)

        # assert area.text == area_name, "Area Mismatch for area_id : {0}, area_name : {1}".format(area_id, area_name)

        area.click()
        # time.sleep(5)
    except:
        return 0

    start_time = time.time()
    while(True):
        # print("inside submit_values")
        end_time = time.time()
        if end_time - start_time > 20:
            print("timeout getting the number of collieries")
            # return 0
        no_of_collieries = len(driver.find_elements_by_xpath(
            "//*[@id = 'colliery_id']/option"))
        if no_of_collieries > 1:
            break

    start_time = time.time()
    while True:
        try:
            # print("inside submit_values")
            end_time = time.time()
            if end_time - start_time > 15:
                print("Timeout getting colliery")
                return 0
            colliery = driver.find_element_by_xpath(
                "//*[@id = 'colliery_id'][1]//*[@value = {}]".format(colliery_id))
            break
        except:
            pass

    # assert colliery.text == colliery_name

    colliery.click()

    print("executing the js")
    driver.execute_script(
        "document.getElementById('start_date').removeAttribute('readonly')")
    driver.execute_script(
        "document.getElementById('end_date').removeAttribute('readonly')")
    driver.execute_script(
        "document.getElementById('form1').removeAttribute('onsubmit')")

    print("done executing js")

    start_date_field = driver.find_element_by_xpath("//*[@id = 'start_date']")
    end_date_field = driver.find_element_by_xpath("//*[@id = 'end_date']")

    start_date_field.clear()
    end_date_field.clear()
    print(start_date, end_date)
    start_date_field.send_keys(start_date)
    end_date_field.send_keys(end_date)

    submit_btn = driver.find_element_by_xpath("//*[@id= 'submit']")
    submit_btn.click()

    return 1


"""
    Enter the start_date and end_date here as needed.
    Enter the date n YYYY-MM-DD format.

    This function then calls scrape_all() for starting and ending date
    defined above.
"""


def scrape_past_dates(start_date="2019-01-03", end_date="2019-01-04"):

    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # assert (end_date_obj - start_date_obj).days <= 7, "Interval of less than equal to seven days allowed"

    return scrape_all2(start_date_obj, end_date_obj)


"""
    This function scrapes the data for one day before.
    It defines start_date and end_date to yesterday's date.
    It then calls scrape_all().
"""


def scrape_yesterday():
    start_date = datetime.datetime.now() - datetime.timedelta(1)
    end_date = start_date

    print("called the function")
    return scrape_all(start_date, end_date)


"""
    It converts datetime object to string.
    returns string
"""


def get_date_string(date):
    format = "%Y-%m-%d"
    date_str = date.strftime(format)

    return date_str


"""
    This function clicks next button on the page till all the results are displayed.
    At every page of the table scrape_rows() is called to extract the data of all the 
    rows from the table.
"""


def scrape_entry_pages():
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


"""
    It extracts the data from the rows in table.
    It returns the extracted data.

    This function is called from scrape_entry_pages()
"""


def scrape_rows():
    columns = driver.find_elements_by_xpath("//*[@role = 'row']")[0]
    column_names = [
        column.text for column in columns.find_elements_by_xpath("./th")]

    rows = driver.find_elements_by_xpath("//*[@role = 'row']")

    data = []
    for row in rows[1:]:
        values = row.find_elements_by_xpath("./td")

        attributes = [value.text for value in values]

        temp_dict = {}
        for (index, attribute) in enumerate(attributes):
            temp_dict[column_names[index]] = attribute

        data.append(temp_dict)

    return data


def insert_data_mongo(data):

    print(data)

    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_password=MONGO_PASS,
        remote_bind_address=('127.0.0.1', 27017)
    )
    print(server)
    server.start()
    print("yaha tak aa gaya")
    client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
    db = client[MONGO_DB]
    # print(db.collection_names())

    coll = db['sales_order_details']
    print(data)
    coll.insert(data)
    with open("log.txt", 'w') as file:
        file.write("Successful insertion")

    server.stop()


def extract_with_bs4(source_code):
    # source_code = driver.page_source
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


"""
    Usage : 

        scrape_past_dates(start_date, end_date)
            Scrape the data from Starting Date to Ending Date

            Arguments:
                start_date : (String) Specify starting date in the format YYYY-MM-DD
                end_date   : (String) Specify end date in the format YYYY-MM-DD
            
            Example : scrape_past_dates(start_date = "2018-12-28", end_date = "2018-12-30")

        scrape_yesterday()
            Scrape the yesterday's data

            Arguments:
                None
            
            Example : scrape_yesterday()
"""
scraped_data = scrape_past_dates(start_date="2019-01-05", end_date="2019-01-06")
# scraped_data = scrape_yesterday()
insert_data_mongo(scraped_data)

with open("scraped_data.json", 'w') as file:
    json.dump(all_area_data, file)

driver.close()

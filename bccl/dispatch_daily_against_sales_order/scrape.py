import requests
from bs4 import BeautifulSoup
import pickle
import datetime

url = "http://www.bcclweb.in/reports/despatch_daily_against_sales_order.php"
sales_order_data = []

def make_calls(sales_order_nums):
    global sales_orders_data
    print(len(sales_orders_data))
    k = 0
    for sales_order_num in sales_order_nums:
        k+=1
        if k % 2 == 0:
            continue
        
        if search(sales_order_num) == 0:
            print("skipping ", sales_order_num)
            continue
        source_code = post_data(sales_order_num)
        # print(source_code)

        sales_order_data = parse_data(source_code, sales_order_num)
        sales_orders_data.append(sales_order_data)
        print(k, ":", sales_order_num, '-', len(sales_order_data), end = ' | ')

        save_data(sales_orders_data)

with open("sales_orders_data1.pickle", "rb") as file:
    sales_orders_data = pickle.load(file)
scraped_sales_orders = {}

for i in sales_orders_data:
    if len(i):
        scraped_sales_orders[i[0]['Sales Order No']] = 1

def search(sales_order_num):
    global scraped_sales_orders
    try:
        if scraped_sales_orders[sales_order_num]:
            return 0
    except:    
        return 1

# def search(sales_order_num):
#     global sales_orders_data
#     with open("sales_orders_data1.pickle", "rb") as file:
#         sales_orders_data = pickle.load(file)

#     for i in sales_orders_data:
#         if len(i) == 0 :continue
#         if i[0]['Sales Order No'] == sales_order_num:
#             return 0
#     return 1

def process(json_data):
    if 'Lifting Date' in json_data:
        json_data['Lifting Date'] = datetime.datetime.strptime(
            json_data['Lifting Date'], "%d-%m-%Y")
    return json_data


def post_data(sales_order_num):


    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"sales_order_no\"\r\n\r\n"+sales_order_num + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"submit\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'Postman-Token': "4c6ebea4-7ffd-4a35-b8be-7b52b0a4ca90"
    }
    response = requests.request("POST", url, data=payload, headers = headers)
    return response.text

def parse_data(source_code, sales_order_num):
    soup = BeautifulSoup(source_code, features='lxml')

    rows = soup.findAll('tr')
    headings_row = rows[0]
    records_rows = rows[1:]

    headings = [heading.text for heading in headings_row.findAll('th')]

    data = []

    for record in records_rows:
        temp_dict = {}
        for index, cell in enumerate(record.findAll('td')):
            temp_dict[headings[index]] = cell.text
        temp_dict['Sales Order No'] = sales_order_num
        temp_dict = process(temp_dict)
        data.append(temp_dict)
        # print(temp_dict)
        # break
    # print(data)
    if len(data) == 0:
        temp = {}
        temp['Sales Order No'] = sales_order_num
        data.append(temp)
    return data

def save_data(sales_orders_data):

    with open("sales_orders_data1.pickle", "wb") as file:
        pickle.dump(sales_orders_data, file)

def scrape():
    with open("sales_order_nums.pickle", "rb") as file:
        sales_order_nums = pickle.load(file)

    make_calls(sales_order_nums)
# def insert_data()

scrape()

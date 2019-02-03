import requests
from bs4 import BeautifulSoup
import pickle, json

def get_consginee_names():
    params = {
        'start_date': "01-01-2018",
        'end_date' : "09-01-2018",
    }

    url = "http://112.133.239.50:8099/ecl_road_sale/get_consignee_ajax.php"

    r = requests.post(url, params)
    consignee_names = r.json()
    consignee_data = {}
    for consignee_id in consignee_names:
        consignee_data[consignee_id] = {
            'so_nums' : get_consignee_so_nums(consignee_id),
            'consignee_name' : consignee_names[consignee_id]
        }
        print(consignee_data)
    with open("area_info.pickle", "wb") as file:
        pickle.dump(consignee_data, file)

        
def get_consignee_so_nums(consginee_id):
    url = "http://112.133.239.50:8099/ecl_road_sale/get_consignee_so_ajax.php"

    params = {
        "start_date" : "01-01-2018",
        "end_date" : "09-01-2018",
        "consignee_code" : consginee_id
    }

    r = requests.post(url, data = params)
    print(r.content, params)
    consignee_so_nums = r.json()

    return list(consignee_so_nums.keys()) 
get_consginee_names()
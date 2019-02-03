import pickle
import requests
from bs4 import BeautifulSoup
import datetime
import time
import random

url = "http://www.centralcoalfields.in/busns/RDOAPP/sodetails.php"

def get_collieries(area_id):
    collieries = []
    url = "http://www.centralcoalfields.in/busns/RDOAPP/getdstrct.php"
    querystring = {"q": area_id}
    response = requests.get(url, params = querystring)
    
    soup = BeautifulSoup(response.text, features='lxml')
    options = soup.findAll('option')

    collieries = [option.text for option in options[1:]]
    print(collieries)
    return collieries
    
def get_areas():
    main_page = requests.get(url)
    source_main_page = main_page.content
    soup = BeautifulSoup(source_main_page)

    all_options = soup.findAll('option')

    all_area_info = {}

    for option in all_options:
        if len(option['value']):
            all_area_info[(option.text, option['value'])] = get_collieries(option['value'])
    with open("area_info.pickle", "wb") as file:
        pickle.dump(all_area_info, file)
get_areas()

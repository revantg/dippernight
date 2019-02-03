"""

    This program exrtacts the names, IDs of the areas and 
    names, IDs of the collieries inside it.

    The information is stored in a pickle file.

    This program need not run every time.
    This program should be run in case a new area or a 
    colliery is added/updated by BCCL.

"""

from selenium import webdriver
import time
import datetime 
import pickle

url = "http://www.bcclweb.in/reports/loading_schedule.php"
driver = webdriver.Firefox(executable_path=r'/home/revant/Downloads/geckodriver-v0.23.0-linux64/geckodriver')
driver.get(url)

areas = driver.find_elements_by_xpath("//*[@name = 'area_id']/option")
area_names = [(area.text, area.get_attribute("value")) for area in areas[1:]]
print (area_names)

area_info = {}
for area in areas[1:]:
    area.click()

    print("sleeping")           
    time.sleep(10)
    print("done")

    collieries = driver.find_elements_by_xpath("//*[@name = 'colliery_id']/option")
    colliery_names = [(i.text, i.get_attribute("value")) for i in collieries[1:]]
   
    area_info[area.text] = {}
    area_info[area.text]['colliery_names'] = colliery_names
    area_info[area.text]['id'] = area.get_attribute("value")

print(area_info)

with open("area_info.pickle", "wb") as file:
    pickle.dump(area_info, file)

driver.close()
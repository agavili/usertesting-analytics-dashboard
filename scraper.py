from bs4 import BeautifulSoup as bs
import requests, re
from lxml import html
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

#SAVE ROUTES

URL = 'https://app.usertesting.com/'
SIGN_IN_ROUTE = 'participants/sign_in'

DASHBOARD_ROUTE = 'my_dashboard/'
COMPLETED_TESTS = 'completed_tests/'


#ACQUIRE WEBDRIVER

s = Service(r'PATH_TO_DRIVER') #download right version of driver
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=s, options=options)

#LOGIN
def login(s, u, p):

    #open participant sign-in page
    driver.get(URL + SIGN_IN_ROUTE)

    #save login values
    email = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    #enter login credentials 
    email.clear()
    email.send_keys(u)
    password.clear()
    password.send_keys(p)

    #target the login button and submit
    button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

login(s,'USERNAME', 'PASSWORD')


#SCRAPE COMPLETED TESTS PAGE FUNCTION

def scrape_completed_tests(arr):
    source = driver.page_source
    soup = bs(source, 'lxml')
    table = soup.find("table", class_="table table--stripe completed-test__table")
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        if(len(row) > 0):
            arr.append(row)
    return arr
    

#SCRAPE VIEW DETAILS FUNCTION

def view_details(devices):
    num_view_details = len(driver.find_elements(By.XPATH,"//table[@class='table table--stripe completed-test__table']//a[.='View details']"))

    for i in range(num_view_details):
        all_tds = driver.find_elements(By.XPATH,"//table[@class='table table--stripe completed-test__table']//a[.='View details']")
        all_tds[i].click()
        devices.append(bs(driver.page_source, 'lxml').find_all("h2")[1].get_text())
        driver.back()
    return devices


#COMPLETED TEST SCRAPING 

l = []
driver.get(URL+DASHBOARD_ROUTE+COMPLETED_TESTS)

#scrape all pages but last 
while len(driver.find_elements(By.XPATH, "//a[text()='Next']")) == 2: 
    l = scrape_completed_tests(l)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Next']"))).click() #Go to next page


# #scrape last page 
l = scrape_completed_tests(l)



#VIEW DETAILS SCRAPING 

d = []
driver.get(URL+DASHBOARD_ROUTE+COMPLETED_TESTS)

#scrape all pages but last 
while len(driver.find_elements(By.XPATH, "//a[text()='Next']")) == 2: 
    d = view_details(d)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Next']"))).click() #Go to next page

#scrape last page 
d = view_details(d)

#CREATE ROUGH UNCLEANED DATAFRAME

df = pd.DataFrame(l, columns=["test_info", "ID", "payment_status", "rating"])
df = df.assign(device = d)
df


#SAVE DATAFRAME TO CSV FOR CLEANING

df.to_csv(r'uncleaned_data.csv', index=False)


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
from time import sleep
from datetime import datetime
import sys

def store(elm, file_name):
    #print(elm.text)
    #start_time = datetime.now()
    file_name = os.path.realpath('.') +"/latest_price/"+file_name + ".txt"
    fileObject = open(file_name, "w")
    fileObject.write(elm.text)
    #time_diff = datetime.now() - start_time
    #print('write completion took -> %s' % time_diff)

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
#options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
# options.headless = True
chromedriver_path = os.path.realpath('.') + "/chromedriver/chromedriver"
driver = webdriver.Chrome(chromedriver_path, options=options)

market = sys.argv[1]
#print('Input argument is '+market)

driver.get("https://coindcx.com/trade/"+market)

try:
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='latest-trade-price']")))
except TimeoutException:
    exit(-1)

#sleep(10)

while True:
    elm = driver.find_element_by_xpath("//span[@class='latest-trade-price']")
    store(elm, market)
    sleep(1)


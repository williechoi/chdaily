import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
import json
from selenium import webdriver
import selenium.common.exceptions
import time

search_item = "전광훈"
base = "http://www.christiandaily.co.kr"
url = "http://www.christiandaily.co.kr/search?q=" + search_item
BASE_URL = "http://www.christiandaily.co.kr"

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(1)
        driver.get(url)
    # res = requests.get(self.url, timeout=10)
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        print(e)
        exit(1)

    # req = requests.get(url)
    # html = req.text
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    result_containers = soup.find_all('div', class_='gs-webResult gs-result')
    print(len(result_containers))
    title_containers = result_containers.find_all('div', class_='gs-title')
    for mytitle in title_containers:
        print(mytitle.href)
        print(mytitle.get_text())


"""
    data = {}

    for title in my_titles:
        print(title.a.text)
        print(title.a.get('href'))
        data[title.a.text] = title.a.get('href')

    with open(os.path.join(BASE_DIR, 'result.json'), 'w+') as json_file:
        json.dump(data, json_file)
"""

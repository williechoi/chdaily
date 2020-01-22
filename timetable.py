
"""
    Cchannel: https://www.cchannel.com/format/format_main?bs_date={YYYY-MM-DD}
    (e.g., https://www.cchannel.com/format/format_main?bs_date=2020-01-24)

    CTS TV: https://www.cts.tv/table?f_yymmdd={YYYY-MM-DD}
    (e.g., https://www.cts.tv/table?f_yymmdd=2020-01-21)

    CBS TV: https://www.cbs.co.kr/tv/timetable/?gubun=&sdate=&cdate={YYYY-MM-DD}
    (e.g., https://www.cbs.co.kr/tv/timetable/?gubun=&sdate=&cdate=2020-01-23)

    GoodTV: http://tv.goodtv.co.kr/schedule.asp?select_date={YYYY-MM-DD}
    (e.g., http://tv.goodtv.co.kr/schedule.asp?select_date=2020-01-23)

    CGN TV: http://www.cgntv.net/center/programschedule.cgn?date={YYYY-MM-DD}
    (e.g., http://www.cgntv.net/center/programschedule.cgn?date=2020-01-22)

"""

from bs4 import BeautifulSoup
import requests
import argparse
from urllib.parse import urljoin, urlparse
import os
import pathlib
from tqdm import tqdm
import re
from selenium import webdriver
import selenium.common.exceptions
import msvcrt
import csv


TIMETABLES = {'CBS':
                  {'url': 'https://www.cbs.co.kr/tv/timetable/',
                   'name': 'CBS TV'},
              'CTS':
                  {'url': 'https://www.cts.tv/table',
                   'name': 'CTS 기독교TV'},
              'CGN':
                  {'url': 'http://www.cgntv.net/center/programschedule.cgn?mode=tv',
                   'name': 'CGN TV'},
              'GoodTV':
                  {'url': 'http://tv.goodtv.co.kr/schedule.asp',
                   'name': 'GoodTV'},
              'Cchannel':
                  {'url': 'https://www.cchannel.com/format/format_main',
                   'name': 'C채널'}
              }

if __name__ == "__main__":
    filename = 'timetable.csv'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    url = "http://www.cchannel.com/format/format_main?bs_date=2020-01-24"
    filepath = os.path.join(BASE_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)

        try:
            driver = webdriver.Chrome('C:\\chromedriver.exe')
            driver.implicitly_wait(3)
            driver.get(url)
        # res = requests.get(self.url, timeout=10)
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(e)
            exit(1)

        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
        except AttributeError as e:
            print(e)
            exit(1)

        rows = soup.find_all('tr')
        for tr in rows:
            data = []
            # for extracting the table heading this will execute only once

            for th in tr.find_all('th'):
                data.append(th.text)

            if data:
                print("Inserting headers: {}".format(','.join(data)))
                csv_writer.writerow(data)
                continue

            for td in tr.find_all('td', class_=['time', 'tit']):
                if td['class'] == 'tit':
                    piece = td.find('span', class_='txt1')
                    print('yahoo')
                    print(piece.text)
                else:
                    print('google')
                    piece = td.text

                data.append(piece)

            if data:
                print("Inserting rows: {}".format(','.join(data)))
                csv_writer.writerow(data)


            # for scraping the actual table data values

            # for td in tr.find_all('td'):
            #     data.append(td.span.text.strip())
            #
            # if data:
            #     print("Inserting Table Data:{}".format(','.join(data)))
            #     csv_writer.writerow(data)









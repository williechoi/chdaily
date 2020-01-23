
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

    unicode whitespaces: \xc2\xa0
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
from datetime import datetime
from datetime import timedelta
import pandas as pd
import re


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


class TVtable:
    base_url_pc = "https://www.naver.com"
    sub_url_pc = "tv/timetable/?gubun=&sdate=&cdate={}"
    base_url_mobile = "https://m.naver.com"
    sub_url_mobile = "tv/timetable/?gubun=&sdate=&cdate={}"
    name = 'TV'
    is_00_to_24 = True
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, now_date, filename='noname.csv'):
        self.now_date = datetime.strptime(now_date, "%Y-%m-%d").date()
        self.next_date = self.now_date + timedelta(days=1)
        self.now_url = urljoin(self.base_url_pc, self.sub_url_pc.format(self.now_date.strftime('%Y-%m-%d')))
        self.next_url = urljoin(self.base_url_pc, self.sub_url_pc.format(self.next_date.strftime('%Y-%m-%d')))
        self.data = []
        self.filename = filename

    def get_selenium_soup(self):
        try:
            driver = webdriver.Chrome('C:\\chromedriver.exe')
            driver.implicitly_wait(3)
            driver.get(self.now_url)
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(e)
            exit(1)

        today_soup = BeautifulSoup(driver.page_source, 'lxml')

        try:
            driver = webdriver.Chrome('C:\\chromedriver.exe')
            driver.implicitly_wait(3)
            driver.get(self.next_url)
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(e)
            exit(1)

        tomorrow_soup = BeautifulSoup(driver.page_source, 'lxml')

        return today_soup, tomorrow_soup


    def get_requests_soup(self):
        res = requests.get(self.now_url)
        if res.status_code == 200:
            html = res.text
        else:
            print("something wrong")
            exit(1)
        today_soup = BeautifulSoup(html, 'lxml')

        res = requests.get(self.next_url)
        if res.status_code == 200:
            html = res.text
        else:
            print("something wrong")
            exit(1)
        tomorrow_soup = BeautifulSoup(html, 'lxml')

        return today_soup, tomorrow_soup

    def get_soup(self):
        if not self.now_url or not self.next_url:
            print("url is not valid!")
            exit(1)

        # today_soup, tomorrow_soup = self.get_requests_soup()
        today_soup, tomorrow_soup = self.get_selenium_soup()

        return today_soup, tomorrow_soup

    def drink(self, soup):
        pass

    def get_dataframe(self):
        if self.is_00_to_24:
            today_df = self.data[0]
            tomorrow_df = self.data[1]
            today_df = today_df[today_df['hour'] >= 4]
            tomorrow_df = tomorrow_df[tomorrow_df['hour'] < 4]
            df = pd.concat((today_df, tomorrow_df), axis=0)

        else:
            df = self.data[0]
        print('a')
        df = df.groupby('hour').agg({self.name: '\n'.join})
        print(df.head())
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'hour'}, inplace=True)
        df['hour'] = df['hour'].apply(lambda x: str(x) + ':00')
        return df

    def export_to_csv(self, df):
        filepath = os.path.join(self.BASE_DIR, self.filename)
        df.to_csv(filepath, index=False)


class CBSTVtable(TVtable):
    base_url_pc = "http://www.cbs.co.kr"
    sub_url_pc = "tv/timetable/?gubun=&sdate=&cdate={}"
    base_url_mobile = "http://m.cbs.co.kr"
    sub_url_mobile = "TV/Timetable.aspx"
    name = 'CBS TV'
    is_00_to_24 = False

    def __init__(self, now_date, filename='cbstv.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        soup = soups[0]
        table = soup.find('div', id='time_data')
        rows = table.find_all('tr')
        all_programs = []
        for tr in rows:
            hour = ""
            minute = ""
            # print(tr)

            for td in tr.find_all('td', class_=['sc_time', 'sc_title']):
                if td['class'][0] == 'sc_time':
                    try:
                        hour = int(td.text.split(':')[0].strip())
                        minute = td.text.split(':')[1].strip()
                    except IndexError as e:
                        print(e)
                        exit(1)
                elif td['class'][0] == 'sc_title':
                    if td.has_attr('a'):
                        prog_name = td.a.text.strip()
                    else:
                        prog_name = td.text.strip()
                    program = '{} {}'.format(minute, prog_name)
                    # print(program)
                    all_programs.append([hour, program])

        self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))


class CTSTVtable(TVtable):
    base_url_pc = "https://www.cts.tv"
    sub_url_pc = "table?f_yymmdd={}"
    base_url_mobile = "https://cts.tv"
    sub_url_mobile = "table/tv?f_yymmdd={}"
    name = 'CTS TV'
    is_00_to_24 = True

    def __init__(self, now_date, filename='ctstv.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        for soup in soups:
            rows = soup.find_all('ul', class_='progTable')
            all_programs = []
            for tr in rows:
                hour = ""
                minute = ""

                for li in tr.find_all('li'):
                    # print(li)
                    for div in li.find_all('div'):
                        if div['class'][0] == 'time':
                            # print('processing time variable')
                            try:
                                hour = int(div.text.split(':')[0].strip())
                                minute = div.text.split(':')[1].strip()
                            except IndexError as e:
                                print(e)
                                exit(1)

                        elif div['class'][0] == 'info':
                            # print('processing program name variable')
                            try:
                                prog_name = div.find('div', class_='title').text.strip()
                            except AttributeError as e:
                                prog_name = 'error'

                            program = '{} {}'.format(minute, prog_name)
                            all_programs.append([hour, program])

                        else:
                            continue

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))


class CGNTVtable(TVtable):
    base_url_pc = "http://www.cgntv.net"
    sub_url_pc = "center/programschedule.cgn?date={}"
    base_url_mobile = "http://m.cgntv.net"
    sub_url_mobile = "center/programschedule.cgn?date={}"
    name = 'CGN TV'
    is_00_to_24 = True

    def __init__(self, now_date, filename='cgntv.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups, filename='noname.csv'):
        for soup in soups:
            rows = soup.find_all('tr')
            all_programs = []
            for tr in rows:
                hour = ""
                minute = ""
                tr.find('td')

                for td in tr.find_all('td'):
                    # print(td)
                    if not td.has_attr('class'):
                        # print('processing time variable')
                        try:
                            hour = int(td.text.split(':')[0])
                            minute = td.text.split(':')[1]
                        except IndexError as e:
                            print(e)
                            exit(1)

                    elif td['class'][0] == 'left':
                        # print('processing program name variable')
                        try:
                            prog_name = td.a.text.strip()
                        except AttributeError as e:
                            prog_name = td.text.strip()

                        prog_name = re.sub(r"[\t\n\r(HD)]", "", prog_name, flags=re.UNICODE)

                        if 'HD' in prog_name:
                            # print('HD found')
                            prog_name.replace('HD', '').strip()

                        program = '{} {}'.format(minute, prog_name)
                        # print(prog_name)
                        all_programs.append([hour, program])
                    else:
                        print('yahoo')

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))


class GoodTVtable(TVtable):
    base_url_pc = "http://tv.goodtv.co.kr"
    sub_url_pc = "schedule.asp?select_date={}"
    base_url_mobile = "http://m.goodtv.co.kr"
    sub_url_mobile = "table.asp?now_date={}"
    name = 'Good TV'
    is_00_to_24 = False

    def __init__(self, now_date, filename='goodtv.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        soup = soups[0]
        rows = soup.find_all('tr')
        all_programs = []
        for tr in rows:
            hour = ""
            minute = ""

            # print(tr)
            for td in tr.find_all('td'):
                if td['class'][0] == 'schedul_con2':
                    # print(td)
                    try:
                        hour = int(td.text.split(':')[0])
                        if hour >= 24:
                            hour = hour - 24
                        minute = td.text.split(':')[1]
                    except IndexError as e:
                        print(e)
                        exit(1)
                elif td['class'][0] == 'schedul_con' and td.text != "":
                    # print(td)
                    prog_name = td.text.strip()
                    program = '{} {}'.format(minute, prog_name)
                    all_programs.append([hour, program])

        self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))


class CchannelTVtable(TVtable):
    base_url_pc = "http://www.cchannel.com"
    sub_url_pc = "format/format_main?bs_date={}"
    base_url_mobile = "http://www.cchannel.com"
    sub_url_mobile = "format/format_main?bs_date={}"
    name = 'Cchannel TV'
    is_00_to_24 = True

    def __init__(self, now_date, filename='cchannel.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        for soup in soups:
            rows = soup.find_all('tr')
            all_programs = []
            for tr in rows:
                hour = ""
                minute = ""

                for td in tr.find_all('td', class_=['time', 'tit']):
                    if td['class'][0] == 'time':
                        # print('processing time variable')
                        try:
                            hour = int(td.text.split(':')[0])
                            minute = td.text.split(':')[1]
                        except IndexError as e:
                            print(e)
                            exit(1)
                        # print('hour = {}\nminutes={}'.format(hour, minute))

                    elif td['class'][0] == 'tit':
                        # print('processing program name variable')
                        # print(td.span.text)
                        prog_name = td.span.text.strip()[:-1]
                        program = '{} {}'.format(minute, prog_name)
                        # print(program)
                        all_programs.append([hour, program])
                    else:
                        pass

                # for hour, prog_name in programs:
                #     print("{} {}".format(hour, prog_name))
                #     # csv_writer.writerow(data)

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))


def export_TVtable(*args, **kwargs):
    is_first = True
    today = kwargs['today']
    for df in args:
        if is_first:
            is_first = False
            final_df = df
        else:
            final_df = pd.merge(df, final_df, on='hour', how='outer')

    final_df = pd.concat([final_df.iloc[4:, :], final_df.iloc[:4, :]], axis=0)

    final_df.to_excel(f'TVtable_{today}.xlsx', encoding='utf-16', sheet_name='sheet1')
    final_df.to_csv(f'TVtable_{today}.csv', encoding='utf-8')


def TVtable(today):
    goodtv = GoodTVtable(today)
    soups = goodtv.get_soup()
    goodtv.drink(soups)
    goodtv_df = goodtv.get_dataframe()
    # goodtv.export_to_csv(goodtv_df)

    ctstv = CTSTVtable(today)
    soups = ctstv.get_soup()
    ctstv.drink(soups)
    cts_df = ctstv.get_dataframe()
    # ctstv.export_to_csv(cts_df)

    cgntv = CGNTVtable(today)
    soups = cgntv.get_soup()
    cgntv.drink(soups)
    cgn_df = cgntv.get_dataframe()
    # cgntv.export_to_csv(cgn_df)

    cchanneltv = CchannelTVtable(today)
    soups = cchanneltv.get_soup()
    cchanneltv.drink(soups)
    cchannel_df = cchanneltv.get_dataframe()
    # cchanneltv.export_to_csv(cchannel_df)

    cbstv = CBSTVtable(today)
    soups = cbstv.get_soup()
    cbstv.drink(soups)
    cbs_df = cbstv.get_dataframe()
    # cbstv.export_to_csv(cbs_df)

    export_TVtable(goodtv_df, cgn_df, cts_df, cbs_df, cchannel_df, today=today)


if __name__ == "__main__":
    TVtable("2020-01-23")
    #
    # goodtv = GoodTVtable("2020-01-23")
    #
    # soups = goodtv.get_soup()
    # goodtv.drink(soups)
    # goodtv.export_to_csv()
    #


    # with open(filepath, 'w', encoding='utf-8') as f:
    #     csv_writer = csv.writer(f)
    #
    #     try:
    #         driver = webdriver.Chrome('C:\\chromedriver.exe')
    #         driver.implicitly_wait(3)
    #         driver.get(url)
    #     # res = requests.get(self.url, timeout=10)
    #     except (TimeoutException, NoSuchElementException, WebDriverException) as e:
    #         print(e)
    #         exit(1)
    #
    #     try:
    #         soup = BeautifulSoup(driver.page_source, 'lxml')
    #     except AttributeError as e:
    #         print(e)
    #         exit(1)

        # rows = soup.find_all('tr')
        # for tr in rows:
        #     data = []
        #     # for extracting the table heading this will execute only once
        #
        #     for th in tr.find_all('th'):
        #         data.append(th.text)
        #
        #     if data:
        #         print("Inserting headers: {}".format(','.join(data)))
        #         csv_writer.writerow(data)
        #         continue
        #
        #     for td in tr.find_all('td', class_=['time', 'tit']):
        #         if td['class'][0] == 'time':
        #             print('amazon')
        #
        #
        #         elif td['class'][0] == 'tit':
        #             print('yahoo')
        #             piece = td.span.txt1.text
        #             piece2 = td.find('span', class_='txt1')
        #             print(piece.text)
        #             print(piece2.text)
        #         else:
        #             print('google')
        #             piece = td.text
        #
        #         data.append(piece)
        #
        #     if data:
        #         print("Inserting rows: {}".format(','.join(data)))
        #         csv_writer.writerow(data)


            # for scraping the actual table data values

            # for td in tr.find_all('td'):
            #     data.append(td.span.text.strip())
            #
            # if data:
            #     print("Inserting Table Data:{}".format(','.join(data)))
            #     csv_writer.writerow(data)










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
from urllib.parse import urljoin
import os
from selenium import webdriver
from datetime import datetime
from datetime import timedelta
import pandas as pd
import re


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
        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(self.now_url)

        today_soup = BeautifulSoup(driver.page_source, 'lxml')

        driver.implicitly_wait(3)
        driver.get(self.next_url)

        tomorrow_soup = BeautifulSoup(driver.page_source, 'lxml')

        return today_soup, tomorrow_soup


    def get_requests_soup(self):
        res = requests.get(self.now_url)
        if res.status_code == 200:
            html = res.text
        else:
            print("something wrong occurred!")
            exit(1)
        today_soup = BeautifulSoup(html, 'lxml')

        res = requests.get(self.next_url)
        if res.status_code == 200:
            html = res.text
        else:
            print("something wrong occurred!")
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
        df = pd.concat((self.data[0], self.data[1]), axis=0)
        df = df.groupby('hour').agg({self.name: '\n'.join})
        return df

    def export_to_csv(self, df):
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'hour'}, inplace=True)
        df['hour'] = df['hour'].apply(lambda x: str(x) + ':00')
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
        is_first_soup = True
        for soup in soups:
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
                        if is_first_soup:
                            if hour != 4:
                                all_programs.append([hour, program])
                        else:
                            if hour == 4:
                                all_programs.append([hour, program])
                    else:
                        continue

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))
            is_first_soup = False


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
        is_first_soup = True
        for soup in soups:
            [s.extract() for s in soup('div', class_='remark')]
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
                            if is_first_soup:
                                if hour > 4:
                                    if hour == 24:
                                        hour = 0
                                    all_programs.append([hour, program])
                            else:
                                if hour < 5:
                                    all_programs.append([hour, program])
                        else:
                            continue

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))
            is_first_soup = False


class CGNTVtable(TVtable):
    base_url_pc = "http://m.cgntv.net"
    sub_url_pc = "center/programschedule.cgn?date={}"
    base_url_mobile = "http://m.cgntv.net"
    sub_url_mobile = "center/programschedule.cgn?date={}"
    name = 'CGN TV'
    is_00_to_24 = True

    def __init__(self, now_date, filename='cgntv.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        is_first_soup = True
        for soup in soups:
            [s.extract() for s in soup('em')]
            rows = soup.find_all('ul', class_='pgr_sch_list')
            all_programs = []
            for tr in rows:
                hour = ""
                minute = ""

                for li in tr.find_all('li'):
                    # print(td)
                    hhmm = li.strong.text
                    try:
                        hour = int(hhmm.split(':')[0])
                        minute = hhmm.split(':')[1]
                    except IndexError as e:
                        print("index error occurred: {}".format(e))
                        exit(1)
                    try:
                        prog_name = li.div.text.strip()
                    except AttributeError as e:
                        print("Attribute Error occurred: {}".format(e))
                        exit(1)

                    prog_name = re.sub(r"([\t\n\r])", "", prog_name, flags=re.UNICODE)

                    if 'HD' in prog_name:
                        # print('HD found')
                        prog_name = prog_name.replace('HD', '').strip()

                    program = '{} {}'.format(minute, prog_name)
                    if is_first_soup:
                        if hour > 4:
                            all_programs.append([hour, program])
                    else:
                        if hour < 5:
                            all_programs.append([hour, program])

                    # script for using PC url. do not use
                    # if not td.has_attr('class'):
                    #     # print('processing time variable')
                    #     try:
                    #         hour = int(td.text.split(':')[0])
                    #         minute = td.text.split(':')[1]
                    #     except IndexError as e:
                    #         print(e)
                    #         exit(1)
                    #
                    # elif td['class'][0] == 'left':
                    #     # print('processing program name variable')
                    #     try:
                    #         prog_name = td.a.text.strip()
                    #     except AttributeError as e:
                    #         prog_name = td.text.strip()
                    #
                    #     prog_name = re.sub(r"([\t\n\r])", "", prog_name, flags=re.UNICODE)
                    #
                    #     if 'HD' in prog_name:
                    #         # print('HD found')
                    #         prog_name = prog_name.replace('HD', '').strip()
                    #
                    #     program = '{} {}'.format(minute, prog_name)
                    #     if is_first_soup:
                    #         if hour > 4:
                    #             all_programs.append([hour, program])
                    #     else:
                    #         if hour < 5:
                    #             all_programs.append([hour, program])
                    #     # print(prog_name)
                    # else:
                    #     continue
                    #     # print('yahoo')

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))
            is_first_soup = False


class GoodTVtable(TVtable):
    base_url_pc = "http://tv.goodtv.co.kr"
    sub_url_pc = "schedule.asp?select_date={}"
    base_url_mobile = "http://m.goodtv.co.kr"
    sub_url_mobile = "table.asp?now_date={}"
    name = 'GoodTV'
    is_00_to_24 = False

    def __init__(self, now_date, filename='goodtv.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        is_first_soup = True
        for soup in soups:
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
                        if is_first_soup:
                            if hour != 4:
                                if hour > 23:
                                    hour = hour - 24
                                all_programs.append([hour, program])
                        else:
                            if hour == 4:
                                all_programs.append([hour, program])
                    else:
                        continue

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))
            is_first_soup = False


class CchannelTVtable(TVtable):
    base_url_pc = "http://www.cchannel.com"
    sub_url_pc = "format/format_main?bs_date={}"
    base_url_mobile = "http://www.cchannel.com"
    sub_url_mobile = "format/format_main?bs_date={}"
    name = 'Cchannel'
    is_00_to_24 = True

    def __init__(self, now_date, filename='cchannel.csv'):
        super().__init__(now_date, filename)

    def drink(self, soups):
        is_first_soup = True
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
                        if is_first_soup:
                            if hour > 4:
                                all_programs.append([hour, program])
                        else:
                            if hour < 5:
                                all_programs.append([hour, program])
                    else:
                        continue

            self.data.append(pd.DataFrame(all_programs, columns=['hour', self.name]))
            is_first_soup = False


def export_TVtable(*args, **kwargs):
    is_first_dataframe = True
    today = kwargs['today']
    for df in args:
        if is_first_dataframe:
            is_first_dataframe = False
            final_df = df
        else:
            final_df = pd.merge(final_df, df, on='hour', how='outer')

    final_df = pd.concat([final_df.iloc[5:, :], final_df.iloc[:5, :]], axis=0)
    final_df = final_df[["CBS TV", "CTS TV", "CGN TV", "GoodTV", "Cchannel"]]

    final_df.reset_index(inplace=True)
    final_df.rename(columns={'index': 'hour'}, inplace=True)
    final_df['hour'] = final_df['hour'].apply(lambda x: str(x) + ':00')
    final_df.rename(columns={"CTS TV": "CTS 기독교TV", "hour": "시간"}, inplace=True)

    final_df.to_excel(f'TVtable_{today}.xlsx', encoding='utf-16', sheet_name=today, index=False)
    final_df.to_csv(f'TVtable_{today}.csv', encoding='utf-8', index=False)


def TVtable(today):
    goodtv = GoodTVtable(today)
    soups = goodtv.get_soup()
    goodtv.drink(soups)
    goodtv_df = goodtv.get_dataframe()

    ctstv = CTSTVtable(today)
    soups = ctstv.get_soup()
    ctstv.drink(soups)
    cts_df = ctstv.get_dataframe()

    cgntv = CGNTVtable(today)
    soups = cgntv.get_soup()
    cgntv.drink(soups)
    cgn_df = cgntv.get_dataframe()

    cchannel = CchannelTVtable(today)
    soups = cchannel.get_soup()
    cchannel.drink(soups)
    cchannel_df = cchannel.get_dataframe()

    cbstv = CBSTVtable(today)
    soups = cbstv.get_soup()
    cbstv.drink(soups)
    cbs_df = cbstv.get_dataframe()

    export_TVtable(goodtv_df, cgn_df, cts_df, cbs_df, cchannel_df, today=today)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', required=False, type=str,
                        default=datetime.today().strftime("%Y-%m-%d"), help='date to extract information')
    values = parser.parse_args()
    TVtable(values.date)
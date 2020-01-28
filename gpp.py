"""
    GodPeople Web Scraper ver. 0.1
    web scraper for benchmarking Godpeople
    for personal use only
    coded by Hyungsuk Choi. ⓒ All rights reserved.
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
import logging
import time
import pandas as pd
from datetime import datetime
from chdaily_general import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class GodPeople():
    original_url = "https://www.godpeople.com/"
    sub_url = ""
    export_dir = os.path.join(BASE_DIR, '갓피플')
    country = "South Korea"
    name = {"KR": "갓피플", "EN": "Godpeople"}


    def __init__(self, page_num):
        self.page_num = page_num
        self.pics = []
        self.main_title = []
        self.sub_title = []
        self.view_cnt = []
        self.cmnt_cnt = []
        self.shr_cnt = []
        self.pub_date = []
        self.main_text = []
        self.scrapped_num = 0
        self.scrapped_page = 0
        self.article_limit = 99999
        self.page_limit = 999

    def page_scrap(self):
        pass

    def article_scrap(self, url):
        pass

    def merge_all_text(self, main_title, sub_title, *main_body_list):
        pass

    def export_data(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        file_name = f'{datetime.today().strftime("%Y-%m-%d")}_{self.name}_분석보고서.csv'
        file_name = get_valid_filename(file_name)
        file_path = os.path.join(self.export_dir, file_name)

        pub_date = pd.Series(self.pub_date)
        main_title = pd.Series(self.main_title)
        sub_title = pd.Series(self.sub_title)
        view_count = pd.Series(self.view_cnt)
        comment_count = pd.Series(self.cmnt_cnt)
        share_count = pd.Series(self.shr_cnt)
        dframe = pd.concat([pub_date, main_title, sub_title, view_count, comment_count, share_count], axis=1)
        dframe.columns = ['date', 'main_title', 'sub_title', 'view_count', 'comment_count', 'share_count']

        dframe.to_csv(file_path, index=False)
        self.export_txt()

    def export_txt(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        for i in range(0, len(self.pub_date)):
            pub_date = self.pub_date[i]
            main_title = self.main_title[i]
            file_name = f'{pub_date}_{self.name}_{main_title}.txt'
            file_name = get_valid_filename(file_name)
            file_path = os.path.join(self.export_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as fout:
                fout.writelines(self.main_text[i])


class GodPeopleTodayTheme(GodPeople):
    original_url = "https://gp.godpeople.com/"
    sub_url = "archives/category/theme/b_theme/page/{}"
    name = "오늘의테마"

    def __init__(self, page_num):
        super().__init__(page_num)

    def page_scrap(self):
        page_url = urljoin(self.original_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                self.scrapped_page += 1
                if self.scrapped_page > self.page_limit or self.scrapped_num > self.article_limit:
                    break
                rows = soup.find_all('div', class_='td-block-row')
                for row in rows:
                    tds = row.find_all('div', class_='td-block-span6')
                    for td in tds:
                        url = td.find('h3').a['href']
                        res = self.article_scrap(url)
                        if not res:
                            print('scrapping failed!')
                            continue
                        else:
                            print('scrapping success!')
                            self.scrapped_num += 1
                            if self.scrapped_num > self.article_limit:
                                raise StopIteration
        except StopIteration:
            pass

        self.export_data()

    def article_scrap(self, url):
        soup = get_single_soup(url)
        main_body_list = []
        if not soup:
            return None

        try:
            main_title = soup.find('h1', class_='entry-title').get_text(strip=True)
        except AttributeError as e:
            print(e)
            main_title = ""

        try:
            sub_title = soup.find('p', class_='td-post-sub-title').get_text(strip=True)
        except AttributeError as e:
            print(e)
            sub_title = ""

        try:
            meta_info = soup.find('div', class_='td-module-meta-info')
        except AttributeError as e:
            print(e)
            pub_date = "1900-01-01"
            view_cnt = -99
            cmnt_cnt = -99
            shr_cnt = -99

        try:
            pub_date = meta_info.find('span', class_='td-post-date').get_text(strip=True)
        except AttributeError as e:
            print(e)
            pub_date = "1900-01-01"

        try:
            view_cnt = int(meta_info.find('div', class_='td-post-views').get_text(strip=True).replace(',', ''))
        except AttributeError as e:
            print(e)
            view_cnt = -99

        try:
            cmnt_cnt = int(meta_info.find('div', class_='td-post-comments').get_text(strip=True).replace(',', ''))
        except AttributeError as e:
            print(e)
            cmnt_cnt = -99

        try:
            shr_cnt = int(meta_info.find('div', class_='td-post-shares').get_text(strip=True).replace(',', ''))
        except AttributeError as e:
            print(e)
            shr_cnt = -99

        try:
            p_tags = soup.find('div', itemprop='articleBody').find_all('p')
            for p_tag in p_tags:
                text = p_tag.get_text('', strip=True)
                text = re.sub(r'[\xa0\n\t\r]', '', text, flags=re.UNICODE)
                main_body_list.append(text)
        except AttributeError as e:
            print(e)

        main_text = self.merge_all_text(main_title, sub_title, *main_body_list)
        self.pub_date.append(pub_date)
        self.main_title.append(main_title)
        self.sub_title.append(sub_title)
        self.view_cnt.append(view_cnt)
        self.cmnt_cnt.append(cmnt_cnt)
        self.shr_cnt.append(shr_cnt)
        self.main_text.append(main_text)
        return 1

    def merge_all_text(self, main_title, sub_title, *main_body_list):
        main_text = ""
        if main_title != "":
            main_text += main_title + "\n\n"

        if sub_title != "":
            main_text += sub_title + "\n\n"

        if main_body_list != []:
            for text in main_body_list:
                main_text += text + "\n"

        return main_text


def main(pag_num):
    # mylogger = logging.getLogger("Choi's logging machine")
    # mylogger.setLevel(logging.INFO)
    # logging.basicConfig(filename='tmp.log', format='%(asctime)s %(message)s')
    # mylogger.log('----------- web scraping started -------------', level=logging.INFO)
    mygodpeople = GodPeopleTodayTheme(pag_num)
    mygodpeople.page_scrap()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', required=False, type=str, default='1', help='Designate the number of pages to be scrapped')
    args = parser.parse_args()

    try:
        page_number = int(args.number)
        if page_number < 1:
            raise ValueError
    except ValueError as e:
        print(e)
        exit(1)

    main(page_number)

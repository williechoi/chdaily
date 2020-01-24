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
from tqdm import tqdm

class Sermon:

    pastor_name = "김준환"
    church_name = "한국교회"
    base_url = "https://www.naver.com"
    sub_url = "tv/timetable/?gubun=&sdate=&cdate={}"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(base_dir, 'sermon')

    filename = 'sermon.csv'

    def __init__(self):
        self.url = urljoin(self.base_url, self.sub_url)
        self.data = []
        self.sermon_files = []

    def download_file(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)

        for num, url in self.sermon_files:
            print(num)
            print(url)
            response = requests.get(url, stream=True)
            file_name = f'{self.church_name} {self.pastor_name} 설교 No. {num}'
            web_name = url.split('/')[-1]
            file_name = os.path.join(self.export_dir, web_name.replace(web_name.split('.')[0], file_name))
            file_size = int(response.headers.get("Content-Length", 0))
            progress = tqdm(response.iter_content(chunk_size=1024), f"Downloading {file_name}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
            with open(file_name, 'wb') as fout:
                for data in progress:
                    fout.write(data)
                    progress.update(len(data))

    def get_soup(self):
        if self.url == "":
            print("URL is required!")
            exit(1)

        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(self.url)

        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
        except AttributeError as e:
            print(e)
            exit(1)

        return soup

    def drink(self, soup):
        pass

    def export_to_csv(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        filepath = os.path.join(self.export_dir, self.filename)
        final_df = pd.concat(self.data, axis=0)
        final_df.to_csv(filepath, index=False)

    def get_valid_title(self, s):
        return s.split(']')[1].strip()

    def get_valid_filename(self, s):
        return re.sub(r'[\\/\:*"<>\|%\$\^&\n]', '', s)


class MannaSermon(Sermon):

    pastor_name = "김병삼"
    church_name = "만나교회"
    base_url = "http://www.manna.or.kr"
    sub_url = "worship/wo_02.php?code=1&subcode=2"
    filename = "manna.csv"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)

    def __init__(self):
        super().__init__()

    def drink(self, soup):
        table = soup.find('table', class_='tbl_news_2')
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        all_sermons = []
        for tr in rows:
            sermon_title = ""
            pastor = ""
            sermon_date = ""
            bible_chapter = ""
            text_url = ""
            try:
                article_num = tr.find('td').get_text()
            except AttributeError as e:
                article_num = "000"
            for td in tr.find_all('dl', class_='sbj_list'):
                sermon_title = self.get_valid_title(td.dt.get_text())
                for dd in td.find_all('dd'):
                    sermon_info = dd.get_text()
                    if sermon_info.startswith("설교자"):
                        pastor = sermon_info.split(":")[1].strip()
                    elif sermon_info.startswith("설교날짜"):
                        sermon_date = sermon_info.split(":")[1].strip()
                    elif sermon_info.startswith("성경본문"):
                        bible_chapter = sermon_info.split(":")[1].strip()
            try:
                sermon_resource = tr.find('td', class_='videoview')
                for aa in sermon_resource.find_all('a'):
                    if aa.img['alt'] == "문서보기":
                        text_url = urljoin(self.base_url, aa['href'])
                        self.sermon_files.append([article_num, text_url])
            except AttributeError as e:
                print(e)

            all_sermons.append([article_num, sermon_title, pastor, sermon_date, bible_chapter, text_url])

        self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))


if __name__ == "__main__":
    manna = MannaSermon()
    soup = manna.get_soup()
    manna.drink(soup)
    manna.export_to_csv()
    manna.download_file()

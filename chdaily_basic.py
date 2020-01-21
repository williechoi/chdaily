"""
    Christian Daily Web Scraper ver. 0.1
    web scraper for christian daily
    for personal use only
    made by Hyungsuk Choi. ⓒ All rights reserved.
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

EXPORT_PATHNAME = "C:\\python_example\\Google_Automation\\output"

class Chdaily:
    original_url = "http://www.christiandaily.co.kr"
    n = 0
#    export_pathname = "C:\\Users\\mj\\Google 드라이브\\0_크로스맵\\0. 기독일보\\지면배치연습\\200121\\"
    
    def __init__(self, url, keyword, order, export_pathname):
        self.url = url
        self.keyword = keyword
        self.order = str(order) + "_"
        self.export_pathname = export_pathname
        self.ch_num = 0
        self.ch_num_2 = 0
        self.paper_num = 0.0
        self.main_body = ""
        self.main_title = ""
        self.sub_title = ""
        self.reporter = ""
        self.main_text = ""
        self.pics = []

    def get_soup(self):
        if self.url == "":
            print("At least one url is required!")
            exit(1)
        else:
            try:
                driver = webdriver.Chrome('C:\\chromedriver.exe')
                driver.implicitly_wait(3)
                driver.get(self.url)
#                res = requests.get(self.url, timeout=10)
            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                print(e)
                exit(1)

            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            except AttributeError as e:
                print(e)
                exit(1)
            return soup

    def get_info(self, soup):
        body_texts = []
        if soup == "":
            print("soup not prepared! boil soup more :P")
            exit(1)
        else:
            # extract maintitle information from soup
            # print(soup)
            try:
                self.main_title = soup.find('h1', {'class': 'article-ttl'}).get_text()
                print("processing {}".format(self.main_title))
                self.cal_num(self.main_title)
            except AttributeError:
                pass

            # extract subtitle information from soup
            try:
                self.sub_title = soup.find('h2', {'class': 'article-sttl'}).get_text()
                self.cal_num(self.sub_title)
            except AttributeError:
                pass

            # extract reporter information from soup
            self.reporter = soup.find('p', {'class': 'art-writer fl'}).get_text().split('(')[0].replace('기독일보', '').strip()

            # extract maintext + mainimage from soup
            image_package = soup.find_all('div', {'class': 'article-txt'})[0].find_all('div', {'class': ['imageBox','imageLeft','imageRight']})
            body_texts_with_tag = soup.find_all('div', {'class': 'article-txt'})[0].find_all('p')

            for txt in image_package:
                img_url = txt.find('img')['src']

                if not self.is_absolute(img_url):
                    img_url = urljoin(self.original_url, img_url)
                try:
                    pos = img_url.index("?")
                    img_url = img_url[:pos]
                except ValueError:
                    pass

                if self.is_valid(img_url):
                    try:
                        caption = txt.find('div', class_='caption').get_text()
                    except ValueError:
                        caption = "내용없음"
#                    print(img_url, caption)
                    self.pics.append([img_url, caption])

            for txt in body_texts_with_tag:
                if txt.find('div', {'class': ['imageBox', 'imageLeft', 'imageRight']}):
                    txt.div.clear()
                    body_texts.append(txt.get_text().strip())

                else:
                    body_texts.append(txt.get_text().strip())

            try:
                for each_text in body_texts:
                    self.main_body += each_text + "\n"
                    self.cal_num(each_text)
            except TypeError as e:
                print(e)
            self.paper_num = self.ch_num_2/200
            if self.reporter != "":
                self.main_body = self.main_body[:-1] + "/" + self.reporter

    def cal_num(self, string):
        if string == "":
            pass

        elif string == "\n":
            self.ch_num += 20
            self.ch_num_2 += 20

        else:
            self.ch_num += len(string) - 1
            self.ch_num_2 += len(string) - 1
            self.ch_num_2 = 20*(self.ch_num_2//20 + 1)

    def is_absolute(self, url):
        """
            Determines whether a 'url' is absolute.
        """
        return bool(urlparse(url).netloc)

    def is_valid(self, url):
        """
            Checks whether 'url' is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def print_res(self):
        print("The number of characters included is: {}".format(self.ch_num))
        print("The number of manuscript papers required is: {}".format(self.paper_num))
        print("The url is: {}".format(self.url))
        print("The keyword to be used is: {}".format(self.keyword))
        print("The main title of this article is: {}".format(self.main_title))
        print("The sub title of this article is: {}".format(self.sub_title))
        print("The body of this article is: {}".format(self.main_body))
        print("The reporter of this article is: {}".format(self.reporter))

    def export_to_txt(self):
        if not os.path.isdir(self.export_pathname):
            os.makedirs(self.export_pathname)

        file_name = '{}{}({}).txt'.format(self.order, self.keyword, self.paper_num, prec='.1')
        file_name = self.get_valid_filename(file_name)
        file_name = os.path.join(self.export_pathname, file_name)
        with open(file_name, 'w', encoding='utf-8') as fout:
            fout.write(self.main_title + "\n\n")
            if self.sub_title != "":
                fout.write(self.sub_title + "\n\n")
            fout.writelines(self.main_body)
#            fout.write("\nnumber of characters: {0}\nnumber of papers: {1}".format(self.ch_num, self.paper_num))

    def download_pic(self):
        if not os.path.isdir(self.export_pathname):
            os.makedirs(self.export_pathname)

        for img_url, file_name in self.pics:
            response = requests.get(img_url, stream=True)
            file_name = '_'.join([self.keyword, file_name])
            file_name = self.get_valid_filename(file_name)
            file_size = int(response.headers.get("Content-Length", 0))
            web_name = img_url.split("/")[-1]
            file_name = os.path.join(self.export_pathname, web_name.replace(web_name.split('.')[0], file_name))
            progress = tqdm(response.iter_content(chunk_size=1024), f"Downloading {file_name}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
            with open(file_name, 'wb') as fout:
                for data in progress:
                    fout.write(data)
                    progress.update(len(data))

    def get_valid_filename(self, s):
        return re.sub(r'[\\/\:*"<>\|%\$\^&]', '', s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyword', required=True, type=str, help='keyword to be used as filename')
    parser.add_argument('-u', '--url', required=True, type=str, help='url for web scraping')
    parser.add_argument('-o', '--order', required=False, default='1', type=str, help='order of article')
    values = parser.parse_args()
    c = input("The current output path: {}\nIf this is incorrect, enter n to exit the application.".format(EXPORT_PATHNAME))
    if c.lower() == 'n':
        exit(1)
    chdaily1 = Chdaily(url=values.url, keyword=values.keyword, order=values.order, export_pathname=EXPORT_PATHNAME)
    soup = chdaily1.get_soup()
    chdaily1.get_info(soup)
    chdaily1.export_to_txt()
    chdaily1.download_pic()

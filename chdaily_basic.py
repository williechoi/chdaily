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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Chdaily:
    original_url = "http://www.christiandaily.co.kr"
    chdaily_garbages = ['Like Us on Facebook\n']
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

    def get_bodytext(self, article):
        body_results = article.find_all('div', class_='article-txt')
        body_text_list = []
        for body_result in body_results:
            body_elements = body_result.find_all('p')
            body_text = '\n'.join([body.text.strip().replace('\n', '') for body in body_elements])
            body_text_list.append(body_text)
        self.main_body = '\n'.join(body_text_list)

    def get_reporter(self, article):
        try:
            self.reporter = article.div.p.a.text
        except AttributeError:
            self.reporter = None

    def get_main_title(self, article):
        try:
            self.main_title = article.h1.text
        except AttributeError:
            self.main_title = None

    def get_sub_title(self, article):
        try:
            self.sub_title = article.h2.text
        except AttributeError:
            self.sub_title = None

    def get_images(self, article):
        images = article.find_all('div', class_=['imageBox', 'imageLeft', 'imageRight'])
        for image in images:
            img_url = image.img['src'].split('?')[0]
            if not self.is_absolute(img_url):
                img_url = urljoin(self.original_url, img_url)
            img_name = image.div.text
            self.pics.append((img_url, img_name))

    def get_main_text(self):
        if self.main_title:
            self.main_text += self.main_title + '\n' + '\n'
        if self.sub_title:
            self.main_text += self.sub_title + '\n' + '\n'
        if self.main_body:
            self.main_text += self.main_body
        if self.reporter:
            self.main_text = self.main_text[:-1] + '/' + self.reporter

    def get_info(self, soup):
        article = soup.find('article')
        self.get_main_title(article)
        self.get_sub_title(article)
        self.get_reporter(article)
        self.get_images(article)
        self.get_bodytext(article)
        self.get_main_text()
        self.cal_num(self.main_text)

#         body_texts = []
#         if soup == "":
#             print("soup not prepared! boil soup more :P")
#             exit(1)
#         else:
#             # extract maintitle information from soup
#             # print(soup)
#             try:
#                 self.main_title = soup.find('h1', {'class': 'article-ttl'}).get_text()
#                 print("processing {}".format(self.main_title))
#                 self.cal_num(self.main_title)
#             except AttributeError:
#                 pass
#
#             # extract subtitle information from soup
#             try:
#                 self.sub_title = soup.find('h2', {'class': 'article-sttl'}).get_text()
#                 self.cal_num(self.sub_title)
#             except AttributeError:
#                 pass
#
#             # extract reporter information from soup
#             self.reporter = soup.find('p', {'class': 'art-writer fl'}).get_text().split('(')[0].replace('기독일보', '').strip()
#
#             # extract maintext + mainimage from soup
#             image_package = soup.find_all('div', {'class': 'article-txt'})[0].find_all('div', {'class': ['imageBox','imageLeft','imageRight']})
#             body_texts_with_tag = soup.find_all('div', {'class': 'article-txt'})[0].find_all('p')
#
#             for txt in image_package:
#                 img_url = txt.find('img')['src']
#
#
#                 try:
#                     pos = img_url.index("?")
#                     img_url = img_url[:pos]
#                 except ValueError:
#                     pass
#
#                 if self.is_valid(img_url):
#                     try:
#                         caption = txt.find('div', class_='caption').get_text()
#                     except ValueError:
#                         caption = "내용없음"
# #                    print(img_url, caption)
#                     self.pics.append([img_url, caption])
#
#             for txt in body_texts_with_tag:
#                 if txt.find('div', {'class': ['imageBox', 'imageLeft', 'imageRight']}):
#                     txt.div.clear()
#                     body_texts.append(txt.get_text().strip())
#
#                 else:
#                     body_texts.append(txt.get_text().strip())
#
#             try:
#                 for each_text in body_texts:
#                     self.main_body += each_text + "\n"
#                     self.cal_num(each_text)
#             except TypeError as e:
#                 print(e)

            # """
            # for garbage_text in self.chdaily_garbages:
            #     if garbage_text in self.main_body:
            #         print('garbage text found!')
            #         self.main_body.replace(garbage_text, '')
            # """
            # if self.reporter != "":
            #     self.main_body = self.main_body[:-1] + "/" + self.reporter

    def cal_num(self, s):
        texts = s.split('\n')
        for text in texts:
            self.ch_num += len(text)
            self.ch_num_2 += len(text)
            self.ch_num_2 = 20 * (self.ch_num_2 // 20 + 1)
        self.paper_num = self.ch_num_2 / 200

    def is_absolute(self, url):
        return bool(urlparse(url).netloc)

    def is_valid(self, url):
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
            fout.writelines(self.main_text)
           # fout.write("\nnumber of characters: {0}\nnumber of papers: {1}".format(self.ch_num, self.paper_num))

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

def main(**kwargs):
    url = kwargs['url']
    keyword = kwargs['keyword']
    order = kwargs['order']
    export_dir = kwargs['export_pathname']
    chdaily1 = Chdaily(url, keyword, order, export_dir)
    soup = chdaily1.get_soup()
    chdaily1.get_info(soup)
    chdaily1.export_to_txt()
    chdaily1.download_pic()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyword', required=True, type=str, help='keyword to be used as filename')
    parser.add_argument('-u', '--url', required=True, type=str, help='url for web scraping')
    parser.add_argument('-o', '--order', required=False, default='1', type=str, help='order of article')
    values = parser.parse_args()
    export_dir = os.path.join(BASE_DIR, 'output')
    main(url=values.url, keyword=values.keyword, order=values.order, export_pathname=export_dir)

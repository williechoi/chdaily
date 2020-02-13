"""
    Christian Daily Web Scraper ver. 0.1
    web scraper for christian daily
    for personal use only
    made by Hyungsuk Choi. ⓒ All rights reserved.
"""

import argparse
import logging
import os
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHDAILY_URLS = {
    "KR-CHDAILY": "https://www.christiandaily.co.kr",
    "US-CHDAILY": "http://kr.christianitydaily.com",
    "KR-NEWSIS": "http://www.newsis.com"
}
EMAIL_RE = re.compile(r'\({0,1}[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}\){0,1}', flags=re.UNICODE)


class Chdaily:
    original_url = "http://www.christiandaily.co.kr"
    country = "Earth"
    name = "기독일보"

    def __init__(self, url, keyword, order, export_dir=os.path.join(BASE_DIR, 'output')):
        self.url = url
        self.keyword = keyword
        self.order = str(order) + "_"
        self.export_dir = export_dir
        self.ch_num = 0
        self.ch_num_2 = 0
        self.paper_num = 0.0
        self.article_number = self.url.split('/')[-1].split('-')[-1].split('.')[0]
        self.main_body = ""
        self.main_title = ""
        self.sub_title = ""
        self.reporter = ""
        self.main_text = ""
        self.pics = []

    def __str__(self):
        return f"""the url of this object is: {self.url}\n
                   the keyword of this object is : {self.keyword}\n
                   the number of characters of this object is : {self.ch_num}\n
                   the number of manuscript papers required is: {self.paper_num}\n
                   the number of this article is: {self.article_number}\n
                   the title of this article is: {self.main_title}\n
                   the subtitle of this article is: {self.sub_title}\n
                   the reporter of this article is: {self.reporter}"""

    def get_soup(self):
        if self.url == "":
            print("At least one url is required!")
            exit(1)

        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(self.url)

        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
        except AttributeError as e:
            print(e)
            exit(1)
        driver.close()

        return soup

    def export_txt_file(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        file_name = '{}{}({}).txt'.format(self.order, self.keyword, self.paper_num, prec='.1')
        file_name = self.get_valid_filename(file_name)
        file_name = os.path.join(self.export_dir, file_name)
        with open(file_name, 'w', encoding='utf-8') as fout:
            fout.writelines(self.main_text)
        logging.info("[{}] {} keyword: {} is now scraped".format(self.article_number, self.name, self.keyword))

    def get_valid_filename(self, s):
        return re.sub(r'[\\/\:*"<>\|%\$\^&\n]', '', s)

    def count_pages(self, s):
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

    def download_image(self):
        i = 1
        filenames = []
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        for img_url, file_name in self.pics:
            response = requests.get(img_url, stream=True)
            file_name = '_'.join([self.keyword, file_name])
            file_name = self.get_valid_filename(file_name)
            if file_name in filenames:
                file_name = f"{file_name} ({i})"
                i += 1
            filenames.append(file_name)
            file_size = int(response.headers.get("Content-Length", 0))
            web_name = img_url.split("/")[-1]
            file_name = os.path.join(self.export_dir, web_name.replace(web_name.split('.')[0], file_name))
            progress = tqdm(response.iter_content(chunk_size=1024), f"Downloading {file_name}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
            with open(file_name, 'wb') as fout:
                for data in progress:
                    fout.write(data)
                    progress.update(len(data))

    def drink(self, soup):
        self.get_main_title(soup)
        self.get_sub_title(soup)
        self.get_reporter_name(soup)
        self.get_images(soup)
        self.get_body_text(soup)
        self.merge_all_text()
        self.count_pages(self.main_text)

    def get_main_title(self, article):
        pass

    def get_sub_title(self, article):
        pass

    def get_reporter_name(self, article):
        pass

    def get_body_text(self, article):
        pass

    def get_images(self, article):
        pass

    def merge_all_text(self):
        pass


class Chdaily_US(Chdaily):
    original_url = "http://kr.christianitydaily.com"
    country = "USA"
    name = "미주 기독일보"

    def __init__(self, url, keyword, order, export_dir=os.path.join(BASE_DIR, 'output')):
        super().__init__(url, keyword, order, export_dir)
        self.article_number = self.url.split('/')[4]

    def get_body_text(self, soup):
        article = soup.find('article')
        body_result = article.find('div', class_='article-txt')

        # remove unwanted texts (e.g., image captions)
        [s.extract() for s in body_result('div')]

        # split body texts into elements of a list
        raw_body_texts = body_result.get_text('\n', strip=True).split('\n')

        # remove unnecessary texts (blank line, Like Us on Facebook) from the list
        # and combine all texts into the single text (main_body)
        for body in raw_body_texts:
            body = re.sub(r'[\n\t\r\xa0]', '', body).strip()
            if body in ['Like Us on', 'Facebook']:
                continue
            elif body == '':
                continue
            else:
                self.main_body = '\n'.join([self.main_body, body])

    def get_reporter_name(self, soup):
        article = soup.find('article')

        # remove unwanted texts (e.g., image captions)
        [s.extract() for s in article('em')]

        # extract reporter name from body
        try:
            self.reporter = article.find('p', class_='art-writer fl').get_text().strip()
        except AttributeError:
            self.reporter = None

        # remove email information
        if re.search(EMAIL_RE, self.reporter):
            self.reporter = re.sub(EMAIL_RE, "", self.reporter).strip()

        # if the name does not contain the word "기자", attach it
        if not self.reporter.endswith('기자'):
            self.reporter = self.reporter + ' 기자'

    def get_main_title(self, soup):
        article = soup.find('article')
        try:
            self.main_title = article.find('h1', class_='article-ttl').get_text().strip()
        except AttributeError:
            self.main_title = None

    def get_sub_title(self, soup):
        article = soup.find('article')
        try:
            self.sub_title = article.find('h2', class_='article-sttl').get_text().strip()
        except AttributeError:
            self.sub_title = None

    def get_images(self, soup):
        article = soup.find('article')
        img_tags = article.find_all('div', class_=['imageBox', 'imageLeft', 'imageRight', 'article-layer'])
        for img_tag in img_tags:
            img_url = img_tag.img['src'].split('?')[0]
            if not self.is_absolute(img_url):
                img_url = urljoin(self.original_url, img_url)
            img_name = img_tag.get_text()
            self.pics.append((img_url, img_name))

    def merge_all_text(self):
        if self.main_title:
            self.main_text += self.main_title + '\n' + '\n'
        if self.sub_title:
            self.main_text += self.sub_title + '\n' + '\n'
        if self.main_body:
            self.main_text += self.main_body
        if self.reporter and self.reporter.strip() != "기자":
            self.main_text = self.main_text + '/' + self.reporter


class Chdaily_KR(Chdaily):
    original_url = "https://www.christiandaily.co.kr"
    country = "South Korea"
    name = "한국 기독일보"
    
    def __init__(self, url, keyword, order, export_dir=os.path.join(BASE_DIR, 'output')):
        super().__init__(url, keyword, order, export_dir)

    def get_body_text(self, soup):
        article = soup.find('article')
        body_result = article.find('div', class_='article-txt')
        # [s.extract() for s in body_results('strong')]
        body_text_list = []

        body_elements_without_ps = body_result.find_all(text=True, recursive=False)
        for i in body_elements_without_ps:
            if i != '\n':
                body_text_list.append(i.strip())
                break

        body_elements = body_result.find_all('p')
        for body in body_elements:
            if re.search(r'\w', body.text):
                sentence = body.text.strip().replace('\n', '')
                body_text_list.append(sentence)

        self.main_body = '\n'.join(body_text_list)

    def get_reporter_name(self, soup):
        article = soup.find('article')
        [s.extract() for s in article('em')]
        try:
            self.reporter = article.find('p', class_='art-writer fl').get_text().strip()
        except AttributeError:
            self.reporter = None
        if re.search(EMAIL_RE, self.reporter):
            self.reporter = re.sub(EMAIL_RE, "", self.reporter).strip()

    def get_main_title(self, soup):
        article = soup.find('article')
        try:
            self.main_title = article.find('h1', class_='article-ttl').get_text().strip()
        except AttributeError:
            self.main_title = None
        # print("main title is: {}".format(self.main_title))

    def get_sub_title(self, soup):
        article = soup.find('article')
        try:
            self.sub_title = article.find('h2', class_='article-sttl').get_text().strip()
        except AttributeError:
            self.sub_title = None
        # print("sub title is: {}".format(self.sub_title))

    def get_images(self, soup):
        article = soup.find('article')
        img_tags = article.find_all('div', class_=['imageBox', 'imageLeft', 'imageRight'])
        for img_tag in img_tags:
            img_url = img_tag.img['src'].split('?')[0]
            if not self.is_absolute(img_url):
                img_url = urljoin(self.original_url, img_url)
            img_name = img_tag.get_text()
            self.pics.append((img_url, img_name))

    def merge_all_text(self):
        if self.main_title:
            self.main_text += self.main_title + '\n' + '\n'
        if self.sub_title:
            self.main_text += self.sub_title + '\n' + '\n'
        if self.main_body:
            self.main_text += self.main_body
        if self.reporter and self.reporter.strip() != "기자":
            self.main_text = self.main_text + '/' + self.reporter


class NewsIs(Chdaily):
    original_url = "https://www.newsis.com"
    country = "South Korea"
    name = "뉴시스"

    def __init__(self, url, keyword, order, export_dir=os.path.join(BASE_DIR, 'output')):
        super().__init__(url, keyword, order, export_dir)

    def get_body_text(self, soup):
        body_text_list = []
        body_result = soup.find('div', id='textBody').find_all(text=True, recursive=False)
        body_text_list = [re.sub(r"\n|\xa0", "", single_text).strip() for single_text in body_result if single_text != '\n']
        body_text = "\n".join(body_text_list[:-1])
        self.main_body = "\n".join(body_text.split("=")[2:]).strip()
        self.reporter = body_text.split("=")[1].split("]")[1].strip()

    def get_reporter_name(self, soup):
        pass

    def get_main_title(self, soup):
        try:
            self.main_title = soup.find('h1').get_text(strip=True)
        except AttributeError:
            self.main_title = None

    def get_sub_title(self, soup):
        article = soup.find('div', id="textBody")
        try:
            self.sub_title = article.find('div', class_='summary_view').get_text('\n', strip=True)
        except AttributeError:
            self.sub_title = None

    def get_images(self, soup):
        def idstartswithtable(id):
            return id and re.compile(r"^imgartitable").match(id)

        img_tags = soup.find_all('table', class_='article_photo', id=idstartswithtable)
        for img_tag in img_tags:
            img_url = img_tag.find('td', class_='img').img['src'].split('?')[0]
            if not self.is_absolute(img_url):
                img_url = urljoin(self.original_url, img_url)
            img_name = img_tag.find('td', class_='desc').get_text(strip=True).split('=')[-1]
            self.pics.append((img_url, img_name))

    def merge_all_text(self):
        if self.main_title:
            self.main_text += self.main_title + '\n' + '\n'
        if self.sub_title:
            self.main_text += self.sub_title + '\n' + '\n'
        if self.main_body:
            self.main_text += self.main_body
        if self.reporter:
            self.main_text = self.main_text + '/' + self.reporter


def main(**kwargs):
    url = kwargs['url']
    keyword = kwargs['keyword']
    order = kwargs['order']


    mylogger = logging.getLogger(__name__)
    mylogger.setLevel(logging.INFO)

    myformatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

    file_handler = logging.FileHandler('tmp.log')
    file_handler.setFormatter(myformatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(myformatter)

    mylogger.addHandler(file_handler)
    mylogger.addHandler(stream_handler)

    mylogger.info('url is: {}\nkeyword is: {}\norder is: {}'.format(url, keyword, order))
    mylogger.info('type: url is {}\nkeyword is: {}\norder is: {}'.format(type(url), type(keyword), type(order)))

    main_url = urlparse(url).netloc

    if main_url in urlparse(CHDAILY_URLS['KR-CHDAILY']).netloc:
        mychdaily = Chdaily_KR(url, keyword, order)
    elif main_url == urlparse(CHDAILY_URLS['US-CHDAILY']).netloc:
        mychdaily = Chdaily_US(url, keyword, order)
    elif main_url == urlparse(CHDAILY_URLS['KR-NEWSIS']).netloc:
        mychdaily = NewsIs(url, keyword, order)
    else:
        print("You entered wrong URL. please try again!")
        exit(1)
    mylogger.info('mychdaily is set to {}'.format(mychdaily.__class__.__name__))

    soup = mychdaily.get_soup()
    mychdaily.drink(soup)
    mychdaily.export_txt_file()
    mychdaily.download_image()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyword', required=True, type=str, help='keyword to be used as filename')
    parser.add_argument('-u', '--url', required=True, type=str, help='url for web scraping')
    parser.add_argument('-o', '--order', required=False, default='1', type=str, help='order of article')
    values = parser.parse_args()
    main(url=values.url, keyword=values.keyword, order=values.order)

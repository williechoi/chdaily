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
import time
from chdaily_general import *

base_dir = os.path.dirname(os.path.abspath(__file__))

class Sermon:
    pastor_name = "김준환"
    base_url = "https://www.naver.com"
    sub_url = "tv/timetable/?gubun=&sdate=&cdate={}"
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)
    church_name = "한국교회"
    filename = 'sermon.csv'

    def __init__(self, page_num, isduplicateallowed):
        self.page_num = page_num
        self.isduplicateallowed = isduplicateallowed
        self.sermon_title = []
        self.bible_chapter = []
        self.sermon_date = []

        self.sub_title = []
        self.sermon_files = []
        self.main_body = []

        self.scrapped_num = 0
        self.scrapped_page = 0

        self.article_limit = 99999
        self.page_limit = 999

    def export_to_hwp(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        file_num = self.date_to_num(self.sermon_date)
        response = requests.get(self.sermon_url, stream=True)
        file_name = f'{file_num}_{self.pastor_name}_{self.sermon_title}.hwp'
        file_name = self.get_valid_filename(file_name)
        web_name = self.sermon_url.split('/')[-1]
        print(web_name)
        file_name = os.path.join(self.export_dir, file_name)
        file_size = int(response.headers.get("Content-Length", 0))
        progress = tqdm(response.iter_content(chunk_size=1024), f"Downloading {file_name}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
        with open(file_name, 'wb') as fout:
            for data in progress:
                fout.write(data)
                progress.update(len(data))

    def get_soup(self, url):
        if url == "":
            print("URL is required!")
            exit(1)

        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(url)
        time.sleep(3)

        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
        except AttributeError as e:
            print(e)
            exit(1)

        driver.close()

        return soup

    def gen_soup(self, num_of_soup=1):
        if num_of_soup < 1 or type(num_of_soup) != int:
            raise ValueError
        for i in range(1, num_of_soup + 1):
            url = urljoin(self.base_url, self.sub_url).format(i)
            driver = webdriver.Chrome('C:\\chromedriver.exe')
            driver.implicitly_wait(3)
            driver.get(url)
            time.sleep(3)

            try:
                soup = BeautifulSoup(driver.page_source, 'lxml')
            except AttributeError as e:
                print(e)
                exit(1)

            driver.close()
            yield soup

    def drink(self):
        pass

    def scrap_sermon(self, sermon_url):
        pass

    def count_pages(self, s):
        char_num = 0
        char_num2 = 0
        paper_num = 0.0
        texts = s.split('\n')
        for text in texts:
            char_num += len(text)
            char_num2 += len(text)
            char_num2 = 20 * (char_num2 // 20 + 1)
        paper_num = char_num2 / 200
        return paper_num

    def export_to_csv(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        filepath = os.path.join(self.export_dir, self.filename)
        final_df = pd.concat(self.data, axis=0)
        final_df.to_csv(filepath, index=False, sep=',')

    def export_to_txt(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        paper_num = self.count_pages(self.main_text)
        file_num = self.date_to_num(self.sermon_date)
        file_name = f'{file_num}_{self.pastor_name}_{self.sermon_title}({paper_num}).txt'
        file_name = self.get_valid_filename(file_name)
        file_name = os.path.join(self.export_dir, file_name)
        with open(file_name, 'w', encoding='utf-8') as fout:
            fout.writelines(self.main_text)

    def get_valid_title(self, s):
        return s.split(']')[1].strip()

    def get_valid_filename(self, s):
        return re.sub(r'[\\/\:*"<>\|%\$\^&\n\"\?]', '', s)

    def merge_all_text(self):
        self.main_text = ""
        if self.sermon_title:
            self.main_text += self.sermon_title + '\n' + '\n'
        if self.bible_chapter:
            self.main_text += self.bible_chapter + '\n' + '\n'
        if self.main_body:
            self.main_text += self.main_body

    def date_to_num(self, d):
        return ''.join(d.split('-'))

    def num_to_date(self, num):
        return '-'.join([num[:4], num[4:6], num[6:]])


class MannaSermon(Sermon):

    pastor_name = "김병삼"
    church_name = "만나교회"
    base_url = "http://www.manna.or.kr"
    sub_url = "worship/wo_02.php?code=1&subcode=2&page={}"
    filename = "manna.csv"
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def page_scrap(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                table = soup.find('table', class_='tbl_news_2')
                tbody = table.find('tbody')
                rows = tbody.find_all('tr')
                all_sermons = []
                for tr in rows:
                    pastor = ""
                    article_num = ""
                    # try:
                    #     article_num = tr.find('td').get_text()
                    # except AttributeError as e:
                    #     article_num = "000"
                    for td in tr.find_all('dl', class_='sbj_list'):
                        self.sermon_title = self.get_valid_title(td.dt.get_text())
                        for dd in td.find_all('dd'):
                            sermon_info = dd.get_text()
                            if sermon_info.startswith("설교자"):
                                pastor = sermon_info.split(":")[1].strip()
                            elif sermon_info.startswith("설교날짜"):
                                self.sermon_date = sermon_info.split(":")[1].strip()
                                article_num = self.date_to_num(self.sermon_date)
                            elif sermon_info.startswith("성경본문"):
                                idx = sermon_info.index(":") + 1
                                self.bible_chapter = sermon_info[idx:].strip()
                    try:
                        sermon_resource = tr.find('td', class_='videoview')
                        for aa in sermon_resource.find_all('a'):
                            if aa.img['alt'] == "문서보기":
                                self.sermon_url = urljoin(self.base_url, aa['href'])
                                self.export_to_hwp()
                    except AttributeError as e:
                        print(e)

                    if self.pastor_name in pastor:
                        all_sermons.append([article_num, self.sermon_title, self.pastor_name, self.sermon_date, self.bible_chapter, self.sermon_url])

                self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))

        except StopIteration:
            pass


class FullGospelSermon(Sermon):

    pastor_name = "조용기"
    church_name = "순복음교회"
    base_url = "http://www.fgnews.co.kr"
    sub_url = "fgN01_1.asp?page={}"
    filename = "fullgospel.csv"
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def page_scrap(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                all_sermons = []
                article_num = ""
                index = 1
                table = soup.select("html>body>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td")
                for td in table:
                    if index % 7 == 1:
                        date_var = td.get_text()
                        date_var = re.sub(r"[\n\t\r\xa0\s]", "", date_var)
                        if date_var == "":
                            break
                        else:
                            self.sermon_date = date_var
                            article_num = self.date_to_num(self.sermon_date)
                    elif index % 7 == 2:
                        self.bible_chapter = td.get_text()
                    elif index % 7 == 3:
                        self.sermon_title = td.get_text()
                    elif index % 7 == 0:
                        try:
                            self.sermon_url = urljoin(self.base_url, td.div.a.get('href'))
                            is_success = self.scrap_sermon(self.sermon_url)
                            if not is_success:
                                continue
                        except AttributeError as e:
                            self.sermon_url = None
                        all_sermons.append([article_num, self.sermon_title, self.pastor_name, self.sermon_date, self.bible_chapter, self.sermon_url])
                    index += 1
                self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))
        except StopIteration:
            pass

    def scrap_sermon(self, sermon_url):
        try:
            soup = self.get_soup(sermon_url)
            main_body = []
            articles = soup.find("span", class_="viewText")
            for article in articles.find_all('p'):
                article_text = article.get_text().strip()
                article_text = re.sub(r"[\t\n\r]", "", article_text, flags=re.UNICODE)
                if article.find("span") is not None:
                    self.sub_title = article_text
                elif article_text == "":
                    continue
                else:
                    main_body.append(article_text)

            self.main_body = '\n'.join(main_body)
            self.merge_all_text()
            self.export_to_txt()
            return True
        except:
            return False

    def merge_all_text(self):
        self.main_text = ""
        if self.sermon_title:
            self.main_text += self.sermon_title + '\n' + '\n'
        if self.sub_title:
            self.main_text += self.sub_title + '\n' + '\n'
        if self.main_body:
            self.main_text += self.main_body

        self.main_text.strip()


class RiverSideSermon(Sermon):

    pastor_name = "김명혁"
    church_name = "강변교회"
    base_url = "http://www.kbpc.kr/jbcgi/board/"
    sub_url = "?p=list&page={}&code=b04"
    filename = "riverside.csv"
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def page_scrap(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                all_sermons = []
                tables = soup.find_all("td")
                for table in tables:
                    rows = table.find_all("td")
                    index = 0
                    for row in rows:
                        if row.text.strip() == "김명혁 목사":
                            self.sermon_title = rows[index-1].get_text().strip()
                            self.sermon_date = rows[index+2].get_text().strip()
                            article_num = self.date_to_num(self.sermon_date)
                            self.sermon_url = urljoin(self.base_url, rows[index-1].div.a.get('href'))
                            self.scrap_sermon(self.sermon_url)
                            all_sermons.append([article_num, self.sermon_title, self.pastor_name, self.sermon_date, self.bible_chapter, self.sermon_url])

                        index += 1

                self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))

        except StopIteration:
            pass

    def scrap_sermon(self, sermon_url):
        soup = self.get_soup(sermon_url)
        main_body = []
        index = 0
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            p_text = re.sub(r"([\t\n\r\xa0])", "", p.text, flags=re.UNICODE)
            if p_text == "" or p_text == "제목이름내용":
                continue
            else:
                if index == 1:
                    self.bible_chapter = p_text
                else:
                    main_body.append(p_text)
            index += 1

        self.main_body = '\n'.join(main_body)
        self.merge_all_text()
        self.export_to_txt()


class TheGreenSermon(Sermon):

    pastor_name = "조성노"
    church_name = "푸른교회"
    base_url = "http://thegreen.or.kr"
    sub_url = "index.php?mid=sermon_m&page={}"
    filename = "thegreen.csv"
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def page_scrap(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                all_sermons = []
                gre = re.compile(r'\[(?P<date>\d+)[a-zA-Z]*\]\s*(?P<title>.+)\s*\((?P<bible>.+)\)')
                rows = soup.find_all("tr")
                for row in rows:
                    if row.parent.name != "tbody":
                        continue
                    else:
                        sermon_tag = row.find("td", class_="title")
                        sermon_info = sermon_tag.get_text(strip=True)
                        m = gre.match(sermon_info)
                        if m is None:
                            continue
                        else:
                            m_dict = m.groupdict()
                            self.sermon_title = m_dict.get('title').strip()
                            self.bible_chapter = m_dict.get('bible').strip()
                            article_num = m_dict.get('date').strip()
                            self.sermon_date = self.num_to_date(article_num)
                            self.sermon_url = urljoin(self.base_url, sermon_tag.a.get('href'))
                            self.scrap_sermon(self.sermon_url)
                            all_sermons.append([article_num, self.sermon_title, self.pastor_name, self.sermon_date, self.bible_chapter, self.sermon_url])

                self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))
        except StopIteration:
            pass

    def scrap_sermon(self, sermon_url):
        soup = self.get_soup(sermon_url)
        main_body = []
        articles = soup.find_all("p", class_="p1")
        for article in articles:
            main_body.append(article.get_text(strip=True))

        self.main_body = "\n".join(main_body[3:])
        self.merge_all_text()
        self.export_to_txt()


class GHPCSermon(Sermon):

    pastor_name = "석기현"
    church_name = "경향교회"
    base_url = "http://www.ghpc.or.kr"
    sub_url = "archives/category/sun01/page/{}"
    filename = "ghpc.csv"
    export_dir = os.path.join(base_dir, 'sermon', pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def page_scrap(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                all_sermons = []
                article_num = "19000101"
                ghre_date = re.compile(r'\d{4}-\d{2}-\d{2}')
                ghre_title = re.compile(r'“.+”')
                video_table = soup.find("div", class_="post_ajax_tm")
                rows = video_table.find_all("div", class_="item-head")
                for row in rows:
                    self.sermon_url = row.h3.a.get('href')
                    sermon_info = row.h3.get_text(strip=True)
                    if "석기현" not in sermon_info:
                        continue
                    else:
                        if re.search(ghre_date, sermon_info):
                            self.sermon_date = re.findall(ghre_date, sermon_info)[0]
                            article_num = self.date_to_num(self.sermon_date)
                        if re.search(ghre_title, sermon_info):
                            self.sermon_title = re.findall(ghre_title, sermon_info)[0]
                        self.scrap_sermon(self.sermon_url)

                    all_sermons.append([article_num, self.sermon_title, self.pastor_name, self.sermon_date, self.bible_chapter, self.sermon_url])

                self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))
        except StopIteration:
            pass

    def scrap_sermon(self, sermon_url):
        soup = self.get_soup(sermon_url)
        main_body = []
        old_body = []
        if self.sermon_title == "":
            try:
                self.sermon_title = soup.find('div', class_="tmr-head").get_text(strip=True)
            except AttributeError as e:
                self.sermon_title = ""

        try:
            self.bible_chapter = soup.find('div', class_='tmr-item').get_text().split('/')[0].strip()
        except IndexError as e:
            self.bible_chapter = ""
        body_texts = soup.find('div', class_='tmr-summary')
        [s.extract() for s in body_texts.find_all('div', align='center')]
        old_body = body_texts.get_text().split('\n')
        for body in old_body:
            body = re.sub(r"([\t\n\r\xa0])", "", body, flags=re.UNICODE)
            if re.search(r'\w', body):
                main_body.append(body)

        self.main_body = '\n'.join(main_body)
        self.merge_all_text()
        self.export_to_txt()

def main(**kwargs):
    pastor_name = kwargs['name']
    page_number = kwargs['number']
    is_duplicates_allowed = kwargs['allowduplicates']
    if pastor_name == "조성노":
        thegreen = TheGreenSermon(page_number, is_duplicates_allowed)
        thegreen.drink()
        thegreen.export_to_csv()

    elif pastor_name == "김명혁":
        riverside = RiverSideSermon(page_number, is_duplicates_allowed)
        riverside.drink()
        riverside.export_to_csv()

    elif pastor_name == "조용기":
        fullgospel = FullGospelSermon(page_number, is_duplicates_allowed)
        fullgospel.drink()
        fullgospel.export_to_csv()

    elif pastor_name == "김병삼":
        manna = MannaSermon(page_number, is_duplicates_allowed)
        manna.drink()
        manna.export_to_csv()

    elif pastor_name == "석기현":
        ghpc = GHPCSermon(page_number, is_duplicates_allowed)
        ghpc.drink()
        ghpc.export_to_csv()

    else:
        print("something wrong!")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pastor', required=True, type=str, help='pastor whose sermon is to be downloaded')
    parser.add_argument('-n', '--number', required=True, type=str, help='number of pages you want to scrap')
    parser.add_argument('-d', '--allowduplicates', required=False, default=True, type=bool, help='whether or not allow downloading duplicates')
    args = parser.parse_args()
    main(name=args.pastor, number=int(args.number), allowduplicates=args.allowduplicates)
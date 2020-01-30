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


class Sermon:
    pastor_name = "김준환"
    church_name = "한국교회"
    base_url = "https://www.naver.com"
    sub_url = "tv/timetable/?gubun=&sdate=&cdate={}"
    export_dir = 'sermon/{}'.format(pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        # arguments
        self.page_num = page_num
        self.isduplicateallowed = isduplicateallowed

        # primary information
        self.sermon_title = []
        self.sermon_date = []
        self.bible_chapter = []
        self.sermon_pastor = []
        self.sermon_url = []

        # progress monitor variable
        self.scrapped_article = 0
        self.scrapped_page = 0
        self.downloaded_file = 0

        # pre-defined limit variable
        self.article_limit = 99999
        self.page_limit = 999

    def scrap_page(self):
        pass

    def scrap_sermon(self, sermon_url):
        pass


class MannaSermon(Sermon):

    pastor_name = "김병삼"
    church_name = "만나교회"
    base_url = "http://www.manna.or.kr"
    sub_url = "worship/wo_02.php?code=1&subcode=2&page={}"
    export_dir = 'sermon/{}'.format(pastor_name)

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def scrap_page(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                if self.scrapped_page >= self.page_limit:
                    break
                table = soup.find('table', class_='tbl_news_2').find('tbody')
                rows = table.find_all('tr')
                for row in rows:
                    sermon_info = row.find('dl', class_='sbj_list')

                    try:
                        sermon_title = sermon_info.dt.get_text(strip=True).split(']')[1].strip()
                    except AttributeError:
                        sermon_title = "만나교회 설교"

                    try:
                        sermon_pastor = sermon_info.find_all('dd')[0].get_text(strip=True).split(":").strip()
                    except AttributeError:
                        sermon_pastor = "정보 없음"

                    try:
                        sermon_date = sermon_info.find_all('dd')[1].get_text(strip=True).split(":").strip()
                        article_num = date_to_num(sermon_date)
                    except AttributeError:
                        sermon_date = "1900-01-01"
                        article_num = 99999999

                    try:
                        idx = sermon_info.find_all('dd')[2].index(":") + 1
                        bible_chapter = sermon_info.find_all('dd')[2].get_text(strip=True)[idx:].strip()
                    except AttributeError:
                        bible_chapter = ""

                    try:
                        sermon_resource = row.find('td', class_='videoview')
                        for a_tag in sermon_resource.find_all('a'):
                            if a_tag.img['alt'] == "문서보기":
                                hwp_url = urljoin(self.base_url, a_tag.get('href'))
                                export_binary_file(hwp_url, header=article_num, primary=sermon_title, secondary=self.pastor_name, extname='hwp', export_dir=self.pastor_name)
                                self.downloaded_file += 1
                    except AttributeError:
                        hwp_url = ""
                        pass

                    self.sermon_date.append(sermon_date)
                    self.sermon_title.append(sermon_title)
                    self.bible_chapter.append(bible_chapter)
                    self.sermon_pastor.append(sermon_pastor)
                    self.sermon_url.append(hwp_url)

                    self.scrapped_article += 1
                    if self.scrapped_article >= self.article_limit:
                        raise StopIteration

                self.scrapped_page += 1

        except StopIteration:
            pass

        finally:
            df = series_to_dataframe([self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url], column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name, secondary="주일설교분석파일", export_dir=self.pastor_name)


class FullGospelSermon(Sermon):

    pastor_name = "조용기"
    church_name = "순복음교회"
    base_url = "http://www.fgnews.co.kr"
    sub_url = "fgN01_1.asp?page={}"
    export_dir = f'sermon/{pastor_name}'

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def scrap_page(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                if self.scrapped_page >= self.page_limit:
                    break

                table = soup.select("html>body>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td")
                for idx, val in enumerate(table, start=1):
                    if idx % 7 == 1:
                        try:
                            sermon_date = re.sub(r'[\n\t\r\xa0\s]', '', val.get_text(strip=True))
                            article_num = date_to_num(sermon_date)
                        except (AttributeError, ValueError):
                            sermon_date = "1900-01-01"
                            article_num = 99999999

                    elif idx % 7 == 2:
                        try:
                            bible_chapter = val.get_text(strip=True)
                        except AttributeError:
                            bible_chapter = ""

                    elif idx % 7 == 3:
                        try:
                            sermon_title = val.get_text(strip=True)
                        except AttributeError:
                            sermon_title = "여의도순복음교회 설교"

                    elif idx % 7 == 0:
                        try:
                            txt_url = urljoin(self.base_url, val.div.a.get('href'))
                            if self.scrap_sermon(txt_url) is not None:
                                self.downloaded_file += 1
                            else:
                                txt_url = ""
                        except AttributeError as e:
                            txt_url = ""
                        if sermon_date != "":
                            self.sermon_date.append(sermon_date)
                            self.sermon_title.append(sermon_title)
                            self.bible_chapter.append(bible_chapter)
                            self.sermon_pastor.append(self.pastor_name)
                            self.sermon_url.append(txt_url)
                            self.scrapped_article += 1

                            if self.scrapped_article >= self.article_limit:
                                raise StopIteration

                self.scrapped_page += 1

        except StopIteration:
            pass

        finally:
            df = series_to_dataframe([self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url], column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name, secondary="주일설교분석파일", export_dir=self.pastor_name)

    def scrap_sermon(self, sermon_url):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        main_body = []

        try:
            main_title = soup.find('span', class_='viewTitle').get_text(strip=True)
        except AttributeError:
            main_title = ""
        sub_title = ""
        try:
            articles = soup.find("span", class_="viewText")
            for article in articles.find_all('p'):
                article_text = re.sub(r"[\t\n\r]", "", article.get_text(strip=True), flags=re.UNICODE)
                if article_text == "":
                    continue
                elif article.find("span") is not None:
                    sub_title = article_text
                else:
                    main_body.append(article_text)

            body_text = '\n'.join(main_body)
        except AttributeError:
            body_text = ""

        main_text = merge_all_text(main_title=main_title, sub_title=sub_title, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name, size=count_page(main_text), export_dir=self.pastor_name)

        return 1


class RiverSideSermon(Sermon):

    pastor_name = "김명혁"
    church_name = "강변교회"
    base_url = "http://www.kbpc.kr/jbcgi/board/"
    sub_url = "?p=list&page={}&code=b04"
    export_dir = f'sermon/{pastor_name}'

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def scrap_page(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                if self.scrapped_page >= self.page_limit:
                    break

                rows = soup.find_all("tr", onmouseout=True)
                for row in rows:
                    cols = row.find_all("td")
                    for idx, val in enumerate(cols):
                        if val.get_text(strip=True) == "김명혁 목사":
                            sermon_title = val[idx-1].get_text(strip=True)
                            sermon_date = val[idx+2].get_text(strip=True)
                            article_num = date_to_num(sermon_date)
                            txt_url = urljoin(self.base_url, rows[idx-1].div.a.get('href'))
                            if self.scrap_sermon(txt_url) is not None:
                                self.downloaded_file += 1
                            else:
                                txt_url = ""

                            self.sermon_date.append(sermon_date)
                            self.sermon_title.append(sermon_title)
                            self.sermon_pastor.append(self.pastor_name)
                            self.sermon_url.append(txt_url)

                            self.scrapped_article += 1
                            if self.scrapped_article >= self.article_limit:
                                raise StopIteration

                self.scrapped_page += 1

        except StopIteration:
            pass

        finally:
            df = series_to_dataframe([self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url], column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name, secondary="주일설교분석파일", export_dir=self.pastor_name)

    def scrap_sermon(self, sermon_url):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        main_body = []
        try:
            articles = soup.find_all('p')
            for idx, val in enumerate(articles):
                article_text = re.sub(r"([\t\n\r\xa0])", "", val.get_text(strip=True), flags=re.UNICODE)
                if article_text == "" or article_text == "제목이름내용":
                    continue
                else:
                    if idx == 1 and len(article_text) < 30:
                        bible_chapter = article_text.strip()
                    elif idx == 0 and len(article_text) < 60:
                        main_title = article_text.strip()
                    else:
                        main_body.append(article_text.strip())

            body_text = '\n'.join(main_body)

        except (AttributeError, ValueError):
            body_text = ""
            bible_chapter = ""

        main_text = merge_all_text(main_title=main_title, sub_title=bible_chapter, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name,size=count_page(main_text), export_dir=self.pastor_name)
        return 1


class TheGreenSermon(Sermon):

    pastor_name = "조성노"
    church_name = "푸른교회"
    base_url = "http://thegreen.or.kr"
    sub_url = "index.php?mid=sermon_m&page={}"
    export_dir = f'sermon\\{pastor_name}'

    def __init__(self, page_num, isduplicateallowed):
        super().__init__(page_num, isduplicateallowed)

    def scrap_page(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                if self.scrapped_page >= self.page_limit:
                    break

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
                            try:
                                sermon_title = m_dict.get('title').strip()
                            except AttributeError as e:
                                print(f'sermon title: {e}')
                                sermon_title = "푸른교회 설교"

                            try:
                                bible_chapter = m_dict.get('bible').strip()
                            except AttributeError as e:
                                print(f'bible chapter: {e}')
                                bible_chapter = ""

                            try:
                                article_num = m_dict.get('date').strip()
                                sermon_date = num_to_date(article_num)
                            except AttributeError:
                                print(f'article num: {e}')
                                sermon_date = "1900-01-01"
                                article_num = 99999999

                            try:
                                txt_url = urljoin(self.base_url, sermon_tag.a.get('href'))
                                if self.scrap_sermon(txt_url, sermon_title, bible_chapter) is not None:
                                    self.downloaded_file += 1
                                else:
                                    txt_url = ""
                            except AttributeError as e:
                                print(f'scrap sermon func: {e}')
                                txt_url = ""

                            self.sermon_date.append(sermon_date)
                            self.bible_chapter.append(bible_chapter)
                            self.sermon_title.append(sermon_title)
                            self.sermon_pastor.append(self.pastor_name)
                            self.sermon_url.append(txt_url)

                            self.scrapped_article += 1
                            if self.scrapped_article >= self.article_limit:
                                raise StopIteration

                self.scrapped_page += 1

        except StopIteration:
            pass

        finally:
            df = series_to_dataframe([self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url], column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name, secondary="주일설교분석파일", export_dir=self.export_dir)


    def scrap_sermon(self, sermon_url, main_title, bible_chapter):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        try:
            main_body = []
            articles = soup.find_all("p", class_="p1")
            for article in articles:
                main_body.append(article.get_text(strip=True))

            body_text = "\n".join(main_body[3:])

        except AttributeError:
            body_text = ""

        main_text = merge_all_text(main_title=main_title, sub_title=bible_chapter, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name, size=count_page(main_text), export_dir=self.export_dir)
        return 1


# class GHPCSermon(Sermon):
#
#     pastor_name = "석기현"
#     church_name = "경향교회"
#     base_url = "http://www.ghpc.or.kr"
#     sub_url = "archives/category/sun01/page/{}"
#     export_dir = f'sermon\\{pastor_name}'
#
#     def __init__(self, page_num, isduplicateallowed):
#         super().__init__(page_num, isduplicateallowed)
#
#     def scrap_page(self):
#         page_url = urljoin(self.base_url, self.sub_url)
#         try:
#             for soup in soup_generator(self.page_num, page_url):
#                 all_sermons = []
#                 article_num = "19000101"
#                 ghre_date = re.compile(r'\d{4}-\d{2}-\d{2}')
#                 ghre_title = re.compile(r'“.+”')
#                 video_table = soup.find("div", class_="post_ajax_tm")
#                 rows = video_table.find_all("div", class_="item-head")
#                 for row in rows:
#                     self.sermon_url = row.h3.a.get('href')
#                     sermon_info = row.h3.get_text(strip=True)
#                     if "석기현" not in sermon_info:
#                         continue
#                     else:
#                         if re.search(ghre_date, sermon_info):
#                             self.sermon_date = re.findall(ghre_date, sermon_info)[0]
#                             article_num = self.date_to_num(self.sermon_date)
#                         if re.search(ghre_title, sermon_info):
#                             self.sermon_title = re.findall(ghre_title, sermon_info)[0]
#                         self.scrap_sermon(self.sermon_url)
#
#                     all_sermons.append([article_num, self.sermon_title, self.pastor_name, self.sermon_date, self.bible_chapter, self.sermon_url])
#
#                 self.data.append(pd.DataFrame(all_sermons, columns=['no', 'title', 'pastor', 'date', 'bible_chapter', 'url']))
#         except StopIteration:
#             pass
#
#     def scrap_sermon(self, sermon_url):
#         soup = self.get_soup(sermon_url)
#         main_body = []
#         old_body = []
#         if self.sermon_title == "":
#             try:
#                 self.sermon_title = soup.find('div', class_="tmr-head").get_text(strip=True)
#             except AttributeError as e:
#                 self.sermon_title = ""
#
#         try:
#             self.bible_chapter = soup.find('div', class_='tmr-item').get_text().split('/')[0].strip()
#         except IndexError as e:
#             self.bible_chapter = ""
#         body_texts = soup.find('div', class_='tmr-summary')
#         [s.extract() for s in body_texts.find_all('div', align='center')]
#         old_body = body_texts.get_text().split('\n')
#         for body in old_body:
#             body = re.sub(r"([\t\n\r\xa0])", "", body, flags=re.UNICODE)
#             if re.search(r'\w', body):
#                 main_body.append(body)
#
#         self.main_body = '\n'.join(main_body)
#         self.merge_all_text()
#         self.export_to_txt()

def main(**kwargs):
    pastor_name = kwargs['name']
    page_number = kwargs['number']
    is_duplicates_allowed = kwargs['allowduplicates']
    if pastor_name == "조성노":
        thegreen = TheGreenSermon(page_number, is_duplicates_allowed)
        thegreen.scrap_page()

    elif pastor_name == "김명혁":
        riverside = RiverSideSermon(page_number, is_duplicates_allowed)
        riverside.scrap_page()

    elif pastor_name == "조용기":
        fullgospel = FullGospelSermon(page_number, is_duplicates_allowed)
        fullgospel.scrap_page()

    elif pastor_name == "김병삼":
        manna = MannaSermon(page_number, is_duplicates_allowed)
        manna.scrap_page()

    #
    # elif pastor_name == "석기현":
    #     ghpc = GHPCSermon(page_number, is_duplicates_allowed)
    #     ghpc.scrap_page()

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
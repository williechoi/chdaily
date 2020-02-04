import argparse

from chdaily_general import *


class Sermon:
    pastor_name = "김준환"
    church_name = "한국교회"
    base_url = "https://www.naver.com"
    sub_url = "tv/timetable/?gubun=&sdate=&cdate={}"
    export_dir = 'sermon\\{}'.format(pastor_name)

    def __init__(self, page_num, isduplicateallowed, limit):
        # arguments
        self.page_num = page_num
        self.isduplicateallowed = isduplicateallowed
        self.article_limit = limit

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
    export_dir = 'sermon\\{}'.format(pastor_name)

    def __init__(self, page_num, isduplicateallowed, limit):
        super().__init__(page_num, isduplicateallowed, limit)

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
                        sermon_pastor = sermon_info.find_all('dd')[0].get_text(strip=True).split(":")[1].strip()
                    except AttributeError:
                        sermon_pastor = "정보 없음"

                    try:
                        sermon_date = sermon_info.find_all('dd')[1].get_text(strip=True).split(":")[1].strip()
                        article_num = date_to_num(sermon_date)
                    except AttributeError:
                        sermon_date = "1900-01-01"
                        article_num = 99999999

                    try:
                        idx = sermon_info.find_all('dd')[2].get_text(strip=True).index(":") + 1
                        bible_chapter = sermon_info.find_all('dd')[2].get_text(strip=True)[idx:].strip()
                    except AttributeError:
                        bible_chapter = ""

                    try:
                        sermon_resource = row.find('td', class_='videoview')
                        for a_tag in sermon_resource.find_all('a'):
                            if a_tag.img['alt'] == "문서보기":
                                hwp_url = urljoin(self.base_url, a_tag.get('href'))
                                export_binary_file(hwp_url, header=article_num, primary=sermon_title,
                                                   secondary=self.pastor_name, extname='hwp',
                                                   export_dir=self.export_dir)
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
            df = series_to_dataframe(
                [self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url],
                column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name,
                            secondary="주일설교분석파일", export_dir=self.export_dir)


class FullGospelSermon(Sermon):
    pastor_name = "조용기"
    church_name = "순복음교회"
    base_url = "http://www.fgnews.co.kr"
    sub_url = "fgN01_1.asp?page={}"
    export_dir = f'sermon\\{pastor_name}'

    def __init__(self, page_num, isduplicateallowed, limit):
        super().__init__(page_num, isduplicateallowed, limit)

    def scrap_page(self):
        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                if self.scrapped_page >= self.page_limit:
                    break

                # table = soup.select("html>body>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td>table>tbody>tr>td")
                rows = soup.find_all('td', width='76')
                for row in rows:
                    sermon_date = "1900-01-01"
                    article_num = 99999999
                    bible_chapter = ""
                    sermon_title = "여의도순복음교회 설교"
                    txt_url = ""

                    try:
                        sermon_date = re.sub(r'[\n\t\r\xa0\s]', '', row.get_text(strip=True))
                        article_num = date_to_num(sermon_date)
                    except (AttributeError, ValueError) as e:
                        print("sermon date: {}".format(e))
                        continue

                    try:
                        bible_chapter = row.parent.find('td', width='115').get_text(strip=True)
                    except AttributeError as e:
                        print("bible chapter: {}".format(e))
                        continue

                    try:
                        sermon_title = row.parent.find('td', width='').get_text(strip=True)
                    except AttributeError as e:
                        print("sermon_title: {}".format(e))
                        continue

                    try:
                        sub_url = row.parent.find('td', width='37').div.a.get('href')
                        txt_url = urljoin(self.base_url, sub_url)
                        if self.scrap_sermon(txt_url) is not None:
                            self.downloaded_file += 1
                    except AttributeError as e:
                        continue

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
            print('iteration stopped because of limit!')

        finally:
            df = series_to_dataframe(
                [self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url],
                column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name,
                            secondary="주일설교분석파일", export_dir=self.export_dir)

    def scrap_sermon(self, sermon_url):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        main_body = []
        main_title = ""
        sub_title = ""
        body_text = ""

        try:
            main_title = soup.find('span', class_='viewTitle').get_text(strip=True)
        except AttributeError:
            pass

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
            pass

        main_text = merge_all_text(main_title=main_title, sub_title=sub_title, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name, size=count_page(main_text),
                        export_dir=self.export_dir)

        return 1


class RiverSideSermon(Sermon):
    pastor_name = "김명혁"
    church_name = "강변교회"
    base_url = "http://www.kbpc.kr/jbcgi/board/"
    sub_url = "?p=list&page={}&code=b04"
    export_dir = f'sermon\\{pastor_name}'

    def __init__(self, page_num, isduplicateallowed, limit):
        super().__init__(page_num, isduplicateallowed, limit)

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
                            try:
                                sermon_title = cols[idx - 1].get_text(strip=True)
                            except AttributeError:
                                sermon_title = ""

                            try:
                                sermon_date = cols[idx + 2].get_text(strip=True)
                                article_num = date_to_num(sermon_date)
                            except AttributeError:
                                sermon_date = "1900-01-01"
                                article_num = 99999999

                            txt_url = urljoin(self.base_url, cols[idx - 1].div.a.get('href'))
                            if self.scrap_sermon(txt_url, sermon_title) is not None:
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
            df = series_to_dataframe(
                [self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url],
                column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name,
                            secondary="주일설교분석파일", export_dir=self.export_dir)

    def scrap_sermon(self, sermon_url, main_title):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        main_body = []
        bible_chapter = ""
        body_text = ""
        try:
            articles = soup.find_all('p')
            for idx, val in enumerate(articles):
                article_text = re.sub(r"([\t\n\r\xa0])", "", val.get_text(strip=True), flags=re.UNICODE)
                if article_text == "" or article_text == "제목이름내용":
                    continue
                else:
                    if idx == 1 and len(article_text) < 30:
                        bible_chapter = article_text.strip()

                    else:
                        main_body.append(article_text.strip())

            body_text = '\n'.join(main_body)

        except (AttributeError, ValueError):
            pass

        self.bible_chapter.append(bible_chapter)
        main_text = merge_all_text(main_title=main_title, sub_title=bible_chapter, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name, size=count_page(main_text),
                        export_dir=self.export_dir)
        return 1


class TheGreenSermon(Sermon):
    pastor_name = "조성노"
    church_name = "푸른교회"
    base_url = "http://thegreen.or.kr"
    sub_url = "index.php?mid=sermon_m&page={}"
    export_dir = f'sermon\\{pastor_name}'

    def __init__(self, page_num, isduplicateallowed, limit):
        super().__init__(page_num, isduplicateallowed, limit)

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
            df = series_to_dataframe(
                [self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url],
                column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name,
                            secondary="주일설교분석파일", export_dir=self.export_dir)

    def scrap_sermon(self, sermon_url, sermon_title, bible_chapter):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        body_text = ""
        try:
            main_body = []
            articles = soup.find_all("p", class_="p1")
            for article in articles:
                main_body.append(article.get_text(strip=True))

            body_text = "\n".join(main_body[3:])

        except AttributeError:
            pass

        main_text = merge_all_text(main_title=sermon_title, sub_title=bible_chapter, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name, size=count_page(main_text),
                        export_dir=self.export_dir)
        return 1


class GHPCSermon(Sermon):
    pastor_name = "석기현"
    church_name = "경향교회"
    base_url = "http://www.ghpc.or.kr"
    sub_url = "archives/category/sun01/page/{}"
    export_dir = f'sermon\\{pastor_name}'

    def __init__(self, page_num, isduplicateallowed, limit):
        super().__init__(page_num, isduplicateallowed, limit)

    def scrap_page(self):
        ghre_date = re.compile(r'\d{4}-\d{2}-\d{2}')
        ghre_title = re.compile(r'“.+”')
        ghre_bible = re.compile(r'(?<=”)[\w\s-]+/')

        page_url = urljoin(self.base_url, self.sub_url)
        try:
            for soup in soup_generator(self.page_num, page_url):
                table = soup.find("div", class_="post_ajax_tm")
                article_num = "19000101"

                rows = table.find_all("div", class_="row")
                for row in rows:
                    cols = row.find_all("div", class_="col-md-3 col-sm-6 col-xs-6")
                    for col in cols:
                        txt_url = ""
                        sermon_date = "1900-01-01"
                        article_num = 99999999
                        sermon_title = "경향교회 설교"
                        bible_chapter = ""

                        val = col.find('div', class_='item-head')

                        try:
                            sermon_info = val.find("h3").get_text(strip=True)

                            if "석기현" not in sermon_info:
                                continue
                            else:
                                if re.search(ghre_date, sermon_info):
                                    sermon_date = re.findall(ghre_date, sermon_info)[0].strip()
                                    article_num = date_to_num(sermon_date)

                                if re.search(ghre_title, sermon_info):
                                    sermon_title = re.findall(ghre_title, sermon_info)[0].strip().replace("“",
                                                                                                          "").replace(
                                        "”", "")

                                if re.search(ghre_bible, sermon_info):
                                    bible_chapter = re.findall(ghre_bible, sermon_info)[0].replace("/", "").strip()

                        except (AttributeError, ValueError):
                            pass

                        try:
                            txt_url = val.find("h3").a['href']
                            if self.scrap_sermon(txt_url, sermon_title, bible_chapter) is not None:
                                self.downloaded_file += 1
                        except (ValueError, AttributeError):
                            pass

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
            df = series_to_dataframe(
                [self.sermon_date, self.sermon_title, self.bible_chapter, self.sermon_pastor, self.sermon_url],
                column_name=['date', 'title', 'bible_chapter', 'pastor', 'url'])
            export_csv_file(df, header=datetime.today().strftime('%Y%m%d'), primary=self.pastor_name,
                            secondary="주일설교분석파일", export_dir=self.export_dir)

    def scrap_sermon(self, sermon_url, sermon_title, bible_chapter):
        soup = get_single_soup(sermon_url)
        if soup is None:
            return None

        main_body = []
        old_body = []

        body_text = ""
        try:
            body_texts = soup.find('div', class_='tmr-summary')
            [s.extract() for s in body_texts.find_all('div', align='center')]
            old_body = body_texts.get_text().split('\n')
            for body in old_body:
                body = re.sub(r"([\t\n\r\xa0])", "", body, flags=re.UNICODE)
                if re.search(r'\w', body):
                    main_body.append(body)

            body_text = '\n'.join(main_body)
        except AttributeError:
            pass

        main_text = merge_all_text(main_title=sermon_title, sub_title=bible_chapter, body_text=body_text)
        export_txt_file(text=main_text, keyword=self.pastor_name, size=count_page(main_text),
                        export_dir=self.export_dir)
        return 1


def class_practice(class_, page_num, is_dupli, lmt):
    myclass = class_(page_num, is_dupli, lmt)
    myclass.scrap_page()


def main(**kwargs):
    pastor_name = kwargs['name']
    page_number = kwargs['number']
    is_duplicates_allowed = kwargs['allowduplicates']
    limit = kwargs['limit']

    if pastor_name == "조성노":
        class_practice(TheGreenSermon, page_number, is_duplicates_allowed, limit)
        # thegreen = TheGreenSermon(page_number, is_duplicates_allowed, limit)
        # thegreen.scrap_page()

    elif pastor_name == "김명혁":
        # class_practice(RiverSideSermon, page_number, is_duplicates_allowed, limit)
        riverside = RiverSideSermon(page_number, is_duplicates_allowed, limit)
        riverside.scrap_page()

    elif pastor_name == "조용기":
        fullgospel = FullGospelSermon(page_number, is_duplicates_allowed, limit)
        fullgospel.scrap_page()

    elif pastor_name == "김병삼":
        manna = MannaSermon(page_number, is_duplicates_allowed, limit)
        manna.scrap_page()

    elif pastor_name == "석기현":
        ghpc = GHPCSermon(page_number, is_duplicates_allowed, limit)
        ghpc.scrap_page()

    else:
        print("something wrong!")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pastor', required=True, type=str, help='pastor whose sermon is to be downloaded')
    parser.add_argument('-n', '--number', required=False, type=int, default=1, help='number of pages you want to scrap')
    parser.add_argument('-d', '--allowduplicates', required=False, default=True, type=bool,
                        help='whether or not allow downloading duplicates')
    parser.add_argument('-l', '--limit', required=False, type=int, default=99999, help='set scrap limit')
    args = parser.parse_args()
    main(name=args.pastor, number=int(args.number), allowduplicates=args.allowduplicates, limit=args.limit)

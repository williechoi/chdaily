
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


import argparse
from datetime import timedelta, datetime

from chdaily_general import *


class TVtable:
    base_url_pc = "https://www.naver.com"
    sub_url_pc = "tv/timetable/?gubun=&sdate=&cdate={}"
    base_url_mobile = "https://m.naver.com"
    sub_url_mobile = "tv/timetable/?gubun=&sdate=&cdate={}"
    name = 'TV'
    is_00_to_24 = True
    export_dir = 'TVtable'

    def __init__(self, now_date):
        # date information
        self.now_date = datetime.strptime(now_date, "%Y-%m-%d").date()
        self.next_date = self.now_date + timedelta(days=1)

        # url information
        self.now_url = urljoin(self.base_url_pc, self.sub_url_pc.format(self.now_date.strftime('%Y-%m-%d')))
        self.next_url = urljoin(self.base_url_pc, self.sub_url_pc.format(self.next_date.strftime('%Y-%m-%d')))

        # data information
        self.hour = []
        self.program = []

    def scrap_table(self):
        pass

    def get_dataframe(self, df):
        return df.groupby('hour').agg({self.name: '\n'.join})


class CBSTVtable(TVtable):
    base_url_pc = "http://www.cbs.co.kr"
    sub_url_pc = "tv/timetable/?gubun=&sdate=&cdate={}"
    base_url_mobile = "http://m.cbs.co.kr"
    sub_url_mobile = "TV/Timetable.aspx"
    name = 'CBS TV'
    is_00_to_24 = False

    def __init__(self, now_date):
        super().__init__(now_date)

    def scrap_table(self):
        soups = [get_single_soup(self.now_url), get_single_soup(self.next_url)]

        for idx, soup in enumerate(soups):
            rows = soup.find('div', id='time_data').find_all('tr')

            for tr in rows:
                hour = ""
                minute = ""

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
                            program = f'{minute} {td.a.text.strip()}'
                        else:
                            program = f'{minute} {td.text.strip()}'

                        if idx == 0 and hour != 4:
                            self.hour.append(hour)
                            self.program.append(program)

                        elif idx == 1 and hour == 4:
                            self.hour.append(hour)
                            self.program.append(program)

                    else:
                        continue

        df = series_to_dataframe([self.hour, self.program], column_name=['hour', self.name])
        df = self.get_dataframe(df)

        return df


class CTSTVtable(TVtable):
    base_url_pc = "https://www.cts.tv"
    sub_url_pc = "table?f_yymmdd={}"
    base_url_mobile = "https://cts.tv"
    sub_url_mobile = "table/tv?f_yymmdd={}"
    name = 'CTS TV'
    is_00_to_24 = True

    def __init__(self, now_date):
        super().__init__(now_date)

    def scrap_table(self):
        soups = [get_single_soup(self.now_url), get_single_soup(self.next_url)]

        for idx, soup in enumerate(soups):
            [s.extract() for s in soup('div', class_='remark')]
            rows = soup.find_all('ul', class_='progTable')

            for tr in rows:
                hour = ""
                minute = ""

                for li in tr.find_all('li'):
                    for div in li.find_all('div'):
                        if div['class'][0] == 'time':
                            try:
                                hour = int(div.text.split(':')[0].strip())
                                minute = div.text.split(':')[1].strip()
                            except IndexError as e:
                                print(e)
                                exit(1)

                        elif div['class'][0] == 'info':
                            try:
                                program = f'{minute} {div.find("div", class_="title").text.strip()}'
                            except AttributeError as e:
                                program = 'error'

                            if idx == 0 and hour > 4:
                                hour = 0 if hour == 24 else hour
                                self.hour.append(hour)
                                self.program.append(program)

                            elif idx == 1 and hour < 5:
                                self.hour.append(hour)
                                self.program.append(program)

                        else:
                            continue

        df = series_to_dataframe([self.hour, self.program], column_name=['hour', self.name])
        df = self.get_dataframe(df)

        return df


class CGNTVtable(TVtable):
    base_url_pc = "http://m.cgntv.net"
    sub_url_pc = "center/programschedule.cgn?date={}"
    base_url_mobile = "http://m.cgntv.net"
    sub_url_mobile = "center/programschedule.cgn?date={}"
    name = 'CGN TV'
    is_00_to_24 = True

    def __init__(self, now_date):
        super().__init__(now_date)
        self.now_url = urljoin(self.base_url_mobile, self.sub_url_mobile.format(self.now_date.strftime('%Y-%m-%d')))
        self.next_url = urljoin(self.base_url_mobile, self.sub_url_mobile.format(self.next_date.strftime('%Y-%m-%d')))

    def scrap_table(self):
        soups = [get_single_soup(self.now_url), get_single_soup(self.next_url)]

        for idx, soup in enumerate(soups):
            [s.extract() for s in soup('em')]
            table = soup.find('ul', class_='pgr_sch_list').find_all('li')

            # return none if TV schedule does not exist
            if table is None:
                print("No schedule")
                return None

            else:
                for li in table:
                    hour = ""
                    minute = ""
                    program = ""

                    hhmm = li.strong.text
                    try:
                        hour = int(hhmm.split(':')[0])
                        minute = hhmm.split(':')[1]
                    except IndexError as e:
                        print("index error occurred: {}".format(e))
                        exit(1)

                    try:
                        prog_name = re.sub(r"([\t\n\r])", "", li.div.text.strip(), flags=re.UNICODE).replace('HD', '').strip()
                        program = f'{minute} {prog_name}'

                    except AttributeError as e:
                        print("Attribute Error occurred: {}".format(e))
                        exit(1)

                    if idx == 0 and hour > 4:
                        self.hour.append(hour)
                        self.program.append(program)

                    elif idx == 1 and hour < 5:
                        self.hour.append(hour)
                        self.program.append(program)

        df = series_to_dataframe([self.hour, self.program], column_name=['hour', self.name])
        df = self.get_dataframe(df)

        return df


class GoodTVtable(TVtable):
    base_url_pc = "http://tv.goodtv.co.kr"
    sub_url_pc = "schedule.asp?select_date={}"
    base_url_mobile = "http://m.goodtv.co.kr"
    sub_url_mobile = "table.asp?now_date={}"
    name = 'GoodTV'
    is_00_to_24 = False

    def __init__(self, now_date):
        super().__init__(now_date)

    def scrap_table(self):
        soups = [get_single_soup(self.now_url), get_single_soup(self.next_url)]

        for idx, soup in enumerate(soups):
            rows = soup.find_all('tr')

            for tr in rows:
                hour = ""
                minute = ""

                for td in tr.find_all('td'):
                    if td['class'][0] == 'schedul_con2':
                        try:
                            hour = int(td.text.split(':')[0])
                            hour = hour - 24 if hour >= 24 else hour
                            minute = td.text.split(':')[1]

                        except IndexError as e:
                            print(e)
                            exit(1)

                    elif td['class'][0] == 'schedul_con' and td.text != "":
                        program = f'{minute} {td.text.strip()}'
                        if idx == 0 and hour != 4:
                            hour = hour - 24 if hour > 23 else hour
                            self.hour.append(hour)
                            self.program.append(program)

                        elif idx == 1 and hour == 4:
                            self.hour.append(hour)
                            self.program.append(program)

                    else:
                        continue

        df = series_to_dataframe([self.hour, self.program], column_name=['hour', self.name])
        df = self.get_dataframe(df)

        return df


class CchannelTVtable(TVtable):
    base_url_pc = "http://www.cchannel.com"
    sub_url_pc = "format/format_main?bs_date={}"
    base_url_mobile = "http://www.cchannel.com"
    sub_url_mobile = "format/format_main?bs_date={}"
    name = 'Cchannel'
    is_00_to_24 = True

    def __init__(self, now_date):
        super().__init__(now_date)


    def scrap_table(self):
        soups = [get_single_soup(self.now_url), get_single_soup(self.next_url)]

        for idx, soup in enumerate(soups):
            table = soup.find('tbody', id="ajaxLoad")
            rows = table.find_all('tr')

            # return None if TV schedule does not exist
            if len(rows) == 1:
                print("no schedule")
                return None

            else:
                for tr in rows:
                    for td in tr.find_all('td', class_=['time', 'tit']):
                        if td['class'][0] == 'time':
                            try:
                                hour = int(td.text.split(':')[0])
                                minute = td.text.split(':')[1]

                            except IndexError as e:
                                print(e)
                                exit(1)

                        elif td['class'][0] == 'tit':
                            program = f'{minute} {td.span.text.strip()[:-1]}'

                            if idx == 0 and hour > 4:
                                self.hour.append(hour)
                                self.program.append(program)

                            elif idx == 1 and hour < 5:
                                self.hour.append(hour)
                                self.program.append(program)
                        else:
                            continue

        df = series_to_dataframe([self.hour, self.program], column_name=['hour', self.name])
        df = self.get_dataframe(df)

        return df


def export_tvtable(dfs, today, export_dir):
    is_first_dataframe = True
    for df in dfs:
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

    export_csv_file(final_df, header='TVtable', primary=today, secondary="요약정리", export_dir=export_dir)
    export_xlsx_file(final_df, header='TVtable', primary=today, secondary="요약정리", export_dir=export_dir)


def tv_class_gen(class_, today):
    myclass = class_(today)
    return myclass.scrap_table()


def main(today):
    tv_df = []
    tv_df.append(tv_class_gen(GoodTVtable, today))
    tv_df.append(tv_class_gen(CTSTVtable, today))
    tv_df.append(tv_class_gen(CGNTVtable, today))
    tv_df.append(tv_class_gen(CchannelTVtable, today))
    tv_df.append(tv_class_gen(CBSTVtable, today))
    export_tvtable(tv_df, today=today, export_dir='TVschedule')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', required=False, type=str, default=datetime.today().strftime("%Y-%m-%d"), help='date to extract information')
    values = parser.parse_args()
    main(values.date)
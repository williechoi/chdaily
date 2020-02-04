import os
import re
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
import time


def selenium(url):
    try:
        if not is_valid_url(url):
            raise ValueError
        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        time.sleep(3)

        # print('soup is well prepared')
    except:
        # print('soup is not well prepared')
        soup = None

    finally:
        driver.close()
        return soup


def get_single_soup(url):
    return selenium(url)


def soup_generator(num, iterable_url, start=1):
    for idx in range(start, num + start):
        url = iterable_url.format(idx)
        yield selenium(url)


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def export_csv_file(df, header, primary, secondary, export_dir):
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_dir)
    file_name = f'{header}_{secondary}_{primary}.csv'
    file_name = get_valid_filename(file_name)
    file_path = get_file_path(export_dir, file_name)

    df.to_csv(file_path, index=False, encoding='utf-8', sep=',')


def export_xlsx_file(df, header, primary, secondary, export_dir):
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_dir)
    file_name = f'{header}_{secondary}_{primary}.xlsx'
    file_name = get_valid_filename(file_name)
    file_path = get_file_path(export_dir, file_name)

    df.to_excel(file_path, index=False, encoding='utf-16', sheet_name=primary)


def export_binary_file(url, header, primary, secondary, extname, export_dir):
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_dir)
    file_name = f'{header}_{secondary}_{primary}.{extname}'
    file_name = get_valid_filename(file_name)
    file_path = get_file_path(export_dir, file_name)

    response = requests.get(url, stream=True)
    file_size = int(response.headers.get("Content-Length", 0))
    progress = tqdm(response.iter_content(chunk_size=1024), f"Downloading {file_name}", total=file_size, unit="B",
                    unit_scale=True, unit_divisor=1024)

    with open(file_path, 'wb') as fout:
        for data in progress:
            fout.write(data)
            progress.update(len(data))


def export_txt_file(text, keyword, size, export_dir):
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_dir)
    file_name = f'{keyword}({size:2.1f}).txt'
    file_name = get_valid_filename(file_name)
    file_path = get_file_path(export_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as fout:
        fout.writelines(text)


def get_file_path(export_dir, file_name):
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)
    return os.path.join(export_dir, file_name)


def date_to_num(d):
    return ''.join(d.split('-'))


def num_to_date(num):
    return '-'.join([num[:4], num[4:6], num[6:]])


def series_to_dataframe(columns, column_name=None):
    series_list = []

    for column in columns:
        series_list.append(pd.Series(column))

    df = pd.concat(series_list, axis=1)
    if df is None:
        print('df is None!')

    if column_name is not None:
        df.columns = column_name

    return df


def get_valid_filename(s):
    return re.sub(r'[\\/\:*"<>\|%\$\^&\n\"\?]', '', s)


def count_page(s):
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


def merge_all_text(main_title, sub_title, body_text):
    main_text = ""
    if main_title:
        main_text += main_title + '\n\n'
    if sub_title:
        main_text += sub_title + '\n\n'
    if body_text:
        main_text += body_text

    main_text = main_text.strip()
    return main_text
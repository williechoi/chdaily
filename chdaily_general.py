import os
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse


def selenium(url):
    try:
        if not is_valid_url(url):
            raise ValueError
        driver = webdriver.Chrome('C:\\chromedriver.exe')
        driver.implicitly_wait(3)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        driver.close()
        return soup
    except:
        return None


def get_single_soup(url):
    return selenium(url)


def soup_generator(num, iterable_url, start=1):
    for idx in range(start, num + start):
        url = iterable_url.format(idx)
        yield selenium(url)


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def export_csv(df, export_dir, file_name):
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)
    filepath = os.path.join(export_dir, file_name)
    df.to_csv(filepath, index=False, sep=',')


def date_to_num(d):
    return ''.join(d.split('-'))


def num_to_date(num):
    return '-'.join([num[:4], num[4:6], num[6:]])


def series_to_dataframe(*columns, column_name=[]):
    series_list = []
    for column in columns:
        series_list.append(pd.Series(column))

    df = pd.concat(series_list, axis=1)
    if not column_name:
        df.columns = column_name

    return df


def get_valid_filename(s):
    return re.sub(r'[\\/\:*"<>\|%\$\^&\n\"\?]', '', s)
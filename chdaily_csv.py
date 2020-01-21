from chdaily_basic import Chdaily
from bs4 import BeautifulSoup
import requests
import argparse
from urllib.parse import urljoin, urlparse
import os
import pathlib
from tqdm import tqdm
import pandas as pd
import numpy as np

EXPORT_PATHNAME = "C:\\Users\\mj\\Google 드라이브\\0_크로스맵\\0. 기독일보\\지면배치연습\\200122\\"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', required=False, default='test1.csv', type=str, help='csv file name to be processed')
    values = parser.parse_args()
    try:
        df = pd.read_csv(values.filename, encoding='utf-8')
    except (FileNotFoundError, SyntaxError) as e:
        print(e)
        exit(1)

    df['order'].fillna(1, inplace=True)
    df['order'] = df['order'].map(lambda x: str(x))

    for index, row in df.iterrows():
        keyword = row['keyword']
        url = row['url']
        order = row['order']
        chdaily1 = Chdaily(url=url, keyword=keyword, order=order, export_pathname=EXPORT_PATHNAME)
        soup = chdaily1.get_soup()
        chdaily1.get_info(soup)
        chdaily1.export_to_txt()
        chdaily1.download_pic()
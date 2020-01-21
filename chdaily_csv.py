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
import time

EXPORT_PATHNAME = "C:\\python_example\\Google_Automation\\output"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', required=False, default='test1.csv', type=str, help='csv file name to be processed')
    values = parser.parse_args()
    c = input("The current output path: {}\nIf this is incorrect, enter n to exit the application.".format(EXPORT_PATHNAME))
    if c.lower() == 'n':
        exit(1)
    try:
        df = pd.read_csv(values.filename, names=['keyword', 'url', 'order'], skiprows=1, encoding='utf-8')
    except (FileNotFoundError, SyntaxError) as e:
        print(e)
        exit(1)

    df['order'].fillna(1, inplace=True)
    df['order'] = df['order'].map(lambda x: str(int(x)))

    for index, row in df.iterrows():
        keyword = row['keyword']
        url = row['url']
        order = row['order']
        chdaily1 = Chdaily(url=url, keyword=keyword, order=order, export_pathname=EXPORT_PATHNAME)
        soup = chdaily1.get_soup()
        chdaily1.get_info(soup)
        chdaily1.export_to_txt()
        chdaily1.download_pic()
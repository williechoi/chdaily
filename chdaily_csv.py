import argparse
import os
import time

import pandas as pd

import chdaily_basic as cb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', required=False, default='test1.csv', type=str, help='csv file name to be processed')
    values = parser.parse_args()
    export_dir = os.path.join(BASE_DIR, 'output')

#    c = input("The current output path: {}\nIf this is incorrect, enter n to exit the application.".format(export_dir))
#    if c.lower() == 'n':
#        exit(1)

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
        cb.main(url=url, keyword=keyword, order=order, export_pathname=export_dir)
        time.sleep(5)

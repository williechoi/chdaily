import requests
from bs4 import BeautifulSoup
import csv
import os

# shortcut for commenting out codes: ctrl + /

URL = "http://www.christiandaily.co.kr/news/%EC%A0%95%EC%9D%98%EB%8B%B9-%EC%8B%AC%EC%83%81%EC%A0%95-%EC%9D%98%EC%9B%90-%EC%B0%A8%EB%B3%84%EA%B8%88%EC%A7%80%EB%B2%95%EC%9C%BC%EB%A1%9C-%EC%B2%98%EB%B2%8C-%EB%90%A0-%EC%88%98-%EC%9E%88%EB%8B%A4-85907.html"
source = requests.get(URL).text

soup = BeautifulSoup(source, 'lxml')

article = soup.find('article')
print(article.prettify())


# body_results = article.find_all('div', class_='article-txt')
#
# for body_result in body_results:
#     body_elements = body_result.find_all('p')
#     body_text = '\n'.join([body.text.strip() for body in body_elements])




# print(body_texts.prettify())

# pic_src = article.find('div', class_=['imageBox', 'imageLeft', 'imageRight']).img['src']
# pos = pic_src.index('?')
# pic_src = pic_src[:pos]
# print(pic_src)

# headline = article.h1.text
# print(headline)
#
# subline = article.h2.text
# print(subline)
#
# reporter = article.div.p.a.text
# print(reporter)

# body = ' '.join([text.strip() for text in article.find_all('div', class_='article-txt').p.text])
# print(body)



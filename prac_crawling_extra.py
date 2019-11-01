import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.sparta_class # db 이름이 sparta_class 입니다.

# 네이버 뉴스 속보 탭 URL
url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001'

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(url, headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')

# selector 예시
#main_content > div.list_body.newsflash_body > ul.type06_headline > li:nth-child(3) > dl > dt.photo > a > img
#main_content > div.list_body.newsflash_body > ul.type06_headline > li:nth-child(1) > dl > dt:nth-child(2) > a
#main_content > div.list_body.newsflash_body > ul.type06_headline > li:nth-child(1) > dl > dd > span.lede
#main_content > div.list_body.newsflash_body > ul.type06_headline > li:nth-child(1) > dl > dd > span.writing

list_selector = "#main_content > div.list_body.newsflash_body > ul.type06_headline > li"
for article in soup.select(list_selector):
    image = article.select_one("dl > dt.photo > a > img")
    description = article.select_one("dl > dd > span.lede")
    news = article.select_one("dl > dd > span.writing")

    # image가 없는 경우 dl > dt > a로 선택, 있는 경우 dt:nth-child(2) > a로 선택
    subject = article.select_one("dl > dt > a")
    if not image == None:
        subject = article.select_one("dt:nth-child(2) > a")
        image = image['src']

    data = {
        'subject': subject.text,
        'image': image,
        'description': description.text,
        'news': news.text
    }

    # collection 이름이 naver_news_crawling
    db.naver_news_crawling.insert_one(data)





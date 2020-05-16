import requests
import json
import re
from bs4 import BeautifulSoup

class HouseCrawler(object):
    def __init__(self, kind=0, mrtline=None, mrtcoods=None, from_price=None, to_price=None):
        self.base_url = "https://rent.591.com.tw"
        self.kind = kind if kind else 0
        self.mrtline = mrtline if kind else 148
        self.mrtcoods = mrtcoods if mrtcoods else 4148
        self.from_price = from_price if from_price else 0
        self.to_price = to_price if to_price else 100000

    def find_pages(self, limit=5):
        page = 0
        all_houses = []
        i = 0
        while True:
            houses = self.find_page(page)
            page += 1
            if not houses:
                break
            print("Get {} data".format(len(houses)))
            all_houses.extend(houses)
            i += 1
            if i == limit:
                break
        return all_houses

    def find_page(self, page=0):
        # Crawl 30 house objects per request
        firstRow = page * 30

        # url = self.base_url + "&".join(["kind=" + str(self.kind), "mrtline=" + str(self.mrtline), "region=1", "mrt=1", "mrtcoods=" + str(self.mrtcoods), "firstRow=" + str(firstRow)])
        url = self.base_url + "/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=4&" + "&".join(["kind=" + str(self.kind), "mrtline=" + str(self.mrtline), "region=1", "mrt=1", "mrtcoods=" + str(self.mrtcoods), "rentprice={},{}".format(self.from_price, self.to_price)])

        print(url)
        headers = {
            'User-Agent': 'PostmanRuntime/7.21.0',
            'Cookie': '591_new_session=eyJpdiI6IitUY0d4SjRDMkdVR3ByVEpGaEkzQkE9PSIsInZhbHVlIjoiZTJzeUpSbGZUMEp6Z3hyMmpEbW9RM3NWbWR2U1R1ajB4Ym1KTDFNOExjQTI5Q0kzWUUxMkFTVndvd2RUVTg2YmYxNHJRemwzYnNhUFowZHM1TnFtYmc9PSIsIm1hYyI6IjFkOWY3MzM2M2Q0YWJmMWZlNWM3ZmMwZGNiMmZhY2EyMDJhMTAzYzU4MjE3M2U5ZDQ0YWFkOWNjNWFiZmNhODYifQ%3D%3D; XSRF-TOKEN=eyJpdiI6ImFoQ2hFYUY5WHVxdVlvUE15YUVRc0E9PSIsInZhbHVlIjoiTnRqNVM1N3kxVEtlbjhtTHIyWVphMHNGVnAydVZ0YTg2RkVic1lsSVRvaFlBWjYyOHRUUDZJZzNLTHBhNFk0U1oreXMrTjdcL3pJdElmZzRSSm9qXC9ZQT09IiwibWFjIjoiYjdhZGQ0YTcyY2Q5YzY1NzMwNmRjNDdmNjlkMWE2NmI5YmQyN2Y1ODg3YWQyYmEyZjM5Nzk4M2RkM2E1MjQ1NyJ9; _ga=GA1.3.1300252815.1586189595; _gid=GA1.3.340574313.1586744292; new_rent_list_kind_test=0; urlJumpIp=1; urlJumpIpByTxt=%E5%8F%B0%E5%8C%97%E5%B8%82; _ga=GA1.4.1300252815.1586189595; _gid=GA1.4.340574313.1586744292; _fbc=fb.2.1586933726781.IwAR287Qghk03edLFqEWV7xg1u0VOFDocRPYLHw58k97OkYS1aFiQAYHxHiOc; _fbp=fb.2.1586189740073.367806070; __asc=8d76e4b217183593be0528335fc; __auc=6ec76bcb1715046a40d7c33ddf5; ba_cid=a%3A5%3A%7Bs%3A6%3A%22ba_cid%22%3Bs%3A32%3A%220414fc2c648f6e645de2edb0522415fe%22%3Bs%3A7%3A%22page_ex%22%3Bs%3A48%3A%22https%3A%2F%2Frent.591.com.tw%2Frent-detail-8986112.html%22%3Bs%3A4%3A%22page%22%3Bs%3A48%3A%22https%3A%2F%2Frent.591.com.tw%2Frent-detail-8986112.html%22%3Bs%3A7%3A%22time_ex%22%3Bi%3A1587046595%3Bs%3A4%3A%22time%22%3Bi%3A1587046609%3B%7D; user_browse_recent=a%3A5%3A%7Bi%3A0%3Ba%3A2%3A%7Bs%3A4%3A%22type%22%3Bi%3A1%3Bs%3A7%3A%22post_id%22%3Bs%3A7%3A%228986112%22%3B%7Di%3A1%3Ba%3A2%3A%7Bs%3A4%3A%22type%22%3Bi%3A1%3Bs%3A7%3A%22post_id%22%3Bs%3A7%3A%229074915%22%3B%7Di%3A2%3Ba%3A2%3A%7Bs%3A4%3A%22type%22%3Bi%3A1%3Bs%3A7%3A%22post_id%22%3Bs%3A7%3A%229122151%22%3B%7Di%3A3%3Ba%3A2%3A%7Bs%3A4%3A%22type%22%3Bi%3A1%3Bs%3A7%3A%22post_id%22%3Bs%3A7%3A%229080238%22%3B%7Di%3A4%3Ba%3A2%3A%7Bs%3A4%3A%22type%22%3Bi%3A1%3Bs%3A7%3A%22post_id%22%3Bs%3A7%3A%229099454%22%3B%7D%7D; user_index_role=1; _gat_rentDetail=1; _gat_rentNew=1; _gat_testUA=1; DETAIL[1][8986112]=1; _dc_gtm_UA-97423186-1=1; _gat=1; is_new_index=1; is_new_index_redirect=1; __utma=82835026.1300252815.1586189595.1587029746.1587029746.1; __utmc=82835026; __utmz=82835026.1587029746.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); c10f3143a018a0513ebe1e8d27b5391c=1; userLoginHttpReferer=https%253A%252F%252Frent.591.com.tw%252F%253Fkind%253D0%2526region%253D1%2526rentprice%253D5000%252C12000; last_search_type=1; tw591__privacy_agree=0; T591_TOKEN=q4mf7o5colpqnss3ostipdo8r1; 591equipment=00363800015861904902649632; TestCookie=1; imgClick=9023798; localTime=2; PHPSESSID=q4mf7o5colpqnss3ostipdo8r1',
            'X-CSRF-TOKEN': 'PFeKMknLZzaKkiG67gMSmMSbKqjdm5LGZRfq497A'
        }
        # url = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=4&mrtline=148&firstRow=0&region=1&mrt=1&mrtcoods=4277"
        res = requests.request("GET", url=url, headers=headers, data={})
        info = json.loads(res.text)

        houses = info["data"]["data"]
        return houses

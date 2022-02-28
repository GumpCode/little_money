#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/12 9:03 下午
# @Author  : ganlinhao

import re
import requests
import json
import datetime
from sqlalchemy import create_engine

from utils.wechat_notice import push_to_wechat


class Client:
    def __init__(self):
        self.engine = create_engine("mysql+pymysql://root@127.0.0.1:3306/fund?charset=utf8")
        self.table = "reminder_history"

    def create_table(self):
        self.engine.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table} ("
            f"'id' INT UNSIGNED AUTO_INCREMENT,"
            f"'time' DATA,"
            f"'code' VARCHAR(10) NOT NULL,"
            f"'nav' FLOAT(5,5) NOT NULL,"
            f"PRIMARY KEY('id')"
            f")ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        )

    def is_today_reminded(self, code, today):
        count = self.engine.execute(f"select count(*) from {self.table} where code={code} and time={today}")
        return True if count >= 1 else False

    def insert_code_record(self, code, time, nav):
        self.engine.execute(
            f"INSET INTO {self.table} (code, nav, time) VALUES ({code}, {nav}, {time});"
        )


class Reminder:
    # */5 18-23 * * 1-5
    def __init__(self):
        self.today = datetime.date.today()
        self.yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.fund_code2name = {"161005": "富国天惠",
                               "163417": "兴全合宜",
                               "163406": "兴全合润"}
        self.sql_client = Client()

    @staticmethod
    def get_price(code):
        url = f"http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&fields=f43" \
              f"&invt=2&secid=0.{code}&cb=jQuery112409040731009806673_1621091370089&_=1621091370091"
        res = requests.get(url)
        return re.findall('"f43":(.*)}}', res.text)[0]

    def get_and_push(self):
        for code in self.fund_code2name:
            if self.sql_client.is_today_reminded(code, self.today):  # 判断今天是否提醒过，提醒过就忽略
                continue
            url = f"https://www.xqfunds.com/fundnetchart.do?fundcode={code}&startDate={self.yesterday}" \
                  f"&endDate={self.today}"
            html = requests.get(url)
            data = re.findall("data:(.*)]", html.text)[2]
            pubdate = re.findall("data : (.*)]", html.text)[0]
            data = json.loads((data + ']').replace("'", '"'))
            pubdate = json.loads((pubdate + ']').replace("'", '"'))
            fund_nav = {date: nav for date, nav in zip(pubdate, data)}
            if self.today in fund_nav:
                price = self.get_price(code=code)
                nav = fund_nav[self.today]
                push_to_wechat(text=f"{self.fund_code2name}净值更新啦!", desp=f"净值{nav}, 溢价{(price-nav)/nav}")
                self.sql_client.insert_code_record(code, self.today, nav)


response = requests.get(url="http://quote.eastmoney.com/sz163406.html")
print(response.text)

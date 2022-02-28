#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/11 10:04 下午
# @Author  : ganlinhao


# 1. 建立股票池和基金对应的数据

# 2. 每天爬取当天的股票池收盘价

# 3. 计算自己模型所得估值

# 4. 当净值更新后，提醒最新净值，同时计算不同平台和自己的模型所对应的差价

import re
import requests
import datetime
import json
import tushare
from sqlalchemy import create_engine

pro = tushare.pro_api('a1b1980392e6299231d1e3b8af1d0c943e536558f2f32bfd5a69ef2d')
engine = create_engine("mysql+pymysql://root@127.0.0.1:3306/fund?charset=utf8")


class FundModel:

    def __init__(self, table_name, code, name, stock, bond, cash, other, total):
        self.table_name = table_name
        self.code = code
        self.name = name
        self.stock = stock
        self.bond = bond
        self.cash = cash
        self.other = other
        self.total = total

    def get_today_price(self):
        today = datetime.datetime.now().strftime('%Y%m%d')
        df = pro.fund_daily(ts_code=(self.code + ".SZ"), start_date=today, end_date=today)
        return float(df.at[0, 'close'])

    def get_yesterday_nav(self, ):
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        df = pro.fund_nav(ts_code=self.code + '.SZ', end_date=yesterday)
        return float(df.at[0, 'unit_nav'])

    @staticmethod
    def is_trade_date():
        """
        返回今天是否是交易日
        :return:
        """
        today = datetime.datetime.now().strftime('%Y%m%d')
        df = pro.trade_cal(exchange='DCE', start_date=today, end_date=today)
        return df.at[0, "is_open"]

    def compute_estimate_value(self, year_stock_path, first_stock_path):
        with open(year_stock_path, 'r', encoding='utf8') as f:
            year_stock = json.load(f)
        with open(first_stock_path, 'r', encoding='utf8') as f:
            first_stock = json.load(f)
        '''
        1. 前十股票选取一季报前十
        2. 剩余的股票采取年报的其他股票
        3. 如果前十的比例已经相较于年报发生变化，那么根据变化的比例对剩余股票进行比例增减持
        '''
        stock_percent = 0.8742
        first_top_10 = sorted(first_stock.items(), key=lambda x: x[1]["index"])[:10]
        for k, v in first_top_10:
            if k in year_stock:
                del year_stock[k]

        total = sum(float(v['percent']) for _, v in first_top_10)
        last_remain_total = sum(float(v['percent']) for _, v in year_stock.items())
        larger = last_remain_total - (stock_percent - total)
        now_stock = {k: v for k, v in first_top_10}
        for k, v in year_stock.items():
            v['percent'] -= v['percent'] / last_remain_total * larger
            now_stock[k] = v

        today = datetime.datetime.now().strftime('%Y%m%d')
        last_nav = pro.fund_nav(ts_code='165509.SZ')
        data = engine.execute(f"select ts_code, close, pre_close from {self.table_name} where trade_date={today}")
        stock_now_percent = 0
        for item in data:
            code, price, pre_close = item
            diff = price / pre_close
            stock_now_percent += now_stock[code[:-3]]['percent'] * diff
            amount = now_stock[code[:-3]]['amount']
            now_stock[code[:-3]]['amount'] = float(''.join(str(amount).split(','))) * diff
        now_stock_amount = self.stock * stock_now_percent / stock_percent
        return last_nav * (now_stock_amount + self.bond + self.cash + self.other) / total

        #print(today, "真实净值", real_today_nav, "估指: ", today_nav, "差值: ", round(real_today_nav - today_nav, 6),
        #      "差值比例: ", round(((real_today_nav - today_nav) / today_nav + offset / index) * 100, 5), "%")
        #offset += (real_today_nav - today_nav) / today_nav

    def import_stock_data(self, stock_path_lst, start_time, end_time):
        if not start_time and not end_time:
            start_time = end_time = datetime.datetime.now().strftime('%Y%m%d')
        all_stock = []
        for path in stock_path_lst:
            with open(path, 'r', encoding='utf8') as f:
                stock = [code for code in json.load(f)]
            all_stock.extend(stock)
        all_stock = set(all_stock)
        for code in all_stock:
            code = code + ".SH" if code.startswith("6") else code + ".SZ"
            data = pro.query("daily", ts_code=code, start_date=start_time, end_date=end_time)
            with engine.begin() as conn:
                data.to_sql(name=self.table_name, con=conn, if_exists='append', index=False)


class Fund406(FundModel):

    def __init__(self):
        super(FundModel).__init__(table_name="", code="163406", name="兴全合润",
                                  stock=23749599191.28, bond=1364435355.28, cash=1956071813.28,
                                  )
        self.today = datetime.datetime.now().strftime('%Y%m%d')
        self.yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")

    def get_today_nav(self):
        url = f"https://www.xqfunds.com/fundnetchart.do?fundcode={self.code}&startDate={self.yesterday}" \
              f"&endDate={self.today}"
        html = requests.get(url)
        data = re.findall("data:(.*)]", html.text)[2]
        pubdate = re.findall("data : (.*)]", html.text)[0]
        data = json.loads((data + ']').replace("'", '"'))[0]
        pubdate = json.loads((pubdate + ']').replace("'", '"').replace("-", ""))[0]
        if pubdate == self.today:
            return float(data)
        else:
            return -1

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/8 9:01 下午
# @Author  : ganlinhao

import time
import json
import requests
from collections import defaultdict
from pprint import pprint


class Fund:
    def __init__(self, activate_fund, etf_fund):

        self.active_fund = activate_fund

        self.etf_fund = etf_fund
        self.active_fund_data = defaultdict()
        self.etf_fund_data = defaultdict()
        for fund_dct, fund_data in [(self.active_fund, self.active_fund_data),
                                    (self.etf_fund, self.etf_fund_data)]:
            for _id, name in fund_dct.items():
                fund_info = {
                    "name": name,
                    "id": _id,
                    "time": None,
                }
                fund_data[_id] = fund_info

    @staticmethod
    def get_current_time():
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class JslFund(Fund):
    def __init__(self, active_fund, etf_fund):
        self.active_url = "https://www.jisilu.cn/data/lof/stock_lof_list/"
        self.etf_url = "https://www.jisilu.cn/data/lof/detail_fund/?___jsl=LST___t=1610095366463"
        super(JslFund, self).__init__(active_fund, etf_fund)

    def get_activate_data(self):
        try:
            response = requests.get(self.active_url)
        except:
            return False

        if not response:
            return False

        res = response.json()['rows']
        for r in res:
            _id = r["id"]
            data = r["cell"]
            if _id in self.active_fund:
                self.active_fund_data[_id]["time"] = self.get_current_time()
                self.active_fund_data[_id]["estimate_value"] = data["estimate_value"]
                self.active_fund_data[_id]["price"] = data["price"]
                self.active_fund_data[_id]["discount_rt"] = data["discount_rt"]
        return True

    def get_etf_data(self):
        try:
            response = requests.get(self.etf_url)
        except:
            return False

        if not response:
            return False

        res = response.json()['rows']
        for r in res:
            _id = r["id"]
            data = r["cell"]
            if _id in self.etf_fund:
                self.etf_fund_data[_id]["time"] = self.get_current_time()
                self.etf_fund_data[_id]["estimate_value"] = data["estimate_value"]
                self.etf_fund_data[_id]["price"] = data["price"]
                self.etf_fund_data[_id]["discount_rt"] = data["discount_rt"]
        return True


class EastMoneyFund(Fund):
    def __init__(self, active_fund, etf_fund):
        super(EastMoneyFund, self).__init__(active_fund, etf_fund)
        self.url = "http://api.fund.eastmoney.com/FundGuZhi/GetFundGZList?type=8&sort=3&orderType=desc&canbuy=0&pageIndex=1&pageSize=20000&callback=jQuery18308633483190352944_1610255803460&_=1610255816167"

    def get_all_data(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Referer": "http://fund.eastmoney.com/"
        }
        try:
            response = requests.get(self.url, headers=headers)
            response.encoding = response.apparent_encoding
            start = response.text.find('{')
            data = json.loads(response.text[start:-1])
        except:
            return False

        if not data:
            return False

        for data in data["Data"]["list"]:
            for fund, fund_data in [(self.active_fund, self.active_fund_data),
                                    (self.etf_fund, self.etf_fund_data)]:
                _id = data["bzdm"]
                if _id in fund_data:
                    fund_data[_id]["estimate_value"] = data["gsz"]
        return True

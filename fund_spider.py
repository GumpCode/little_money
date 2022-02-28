#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/11 9:43 下午
# @Author  : ganlinhao

import time
import json
import tushare
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root@127.0.0.1:3306/fund?charset=utf8")


year_stock_path = "data/163406/year_stock_163406.json"
year_bond_path = "data/163406/year_bond_163406.json"
year_pdf_path = "data/2020-12.pdf"

first_stock_path = "data/163406/first_stock_163406.json"
first_bond_path = "data/163406/first_bond_163406.json"
first_pdf_path = "data/2021-03.pdf"

pro = tushare.pro_api('a1b1980392e6299231d1e3b8af1d0c943e536558f2f32bfd5a69ef2d')


with open(year_stock_path, 'r', encoding='utf8') as f1, \
        open(year_bond_path, 'r', encoding='utf8') as f2:
    year_stock = json.load(f1)
    year_bond = json.load(f2)

with open(first_stock_path, 'r', encoding='utf8') as f1, \
        open(first_bond_path, 'r', encoding='utf8') as f2:
    first_stock = json.load(f1)
    first_bond = json.load(f2)

# 20210401 -- 20210511
start_time = "20210401"
end_time = "20210528"
all_stock = set([code for code in first_stock] + [code for code in year_stock])
for code in all_stock:
    code = code + ".SH" if code.startswith("6") else code + ".SZ"
    data = pro.query("daily", ts_code=code, start_date=start_time, end_date=end_time)
    print(data)
    exit(0)
    with engine.begin() as conn:
        data.to_sql(name="history", con=conn, if_exists='append', index=False)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/11 10:53 下午
# @Author  : ganlinhao


import json
import datetime
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root@127.0.0.1:3306/fund?charset=utf8")

year_stock_path = "data/163406/year_stock_163406.json"
year_bond_path = "data/163406/year_bond_163406.json"
first_stock_path = "data/163406/first_stock_163406.json"
first_bond_path = "data/163406/first_bond_163406.json"

fund_nav_dict = {}
with open("data/fund", 'r', encoding='utf8') as f:
    for line in f.readlines():
        date, nav = line.strip().split("\t")
        fund_nav_dict[date] = float(nav)

with open(year_stock_path, 'r', encoding='utf8') as f1, \
        open(year_bond_path, 'r', encoding='utf8') as f2:
    year_stock = json.load(f1)
    year_bond = json.load(f2)

with open(first_stock_path, 'r', encoding='utf8') as f1, \
        open(first_bond_path, 'r', encoding='utf8') as f2:
    first_stock = json.load(f1)
    first_bond = json.load(f2)


stock_percent = 0.8742
bond_percent = 0.0502
cash_percent = 0.072
top_10 = {}
year_top_10 = sorted(year_stock.items(), key=lambda x: x[1]["index"])[:10]
first_top_10 = sorted(first_stock.items(), key=lambda x: x[1]["index"])[:10]


'''
1. 前十股票选取一季报前十
2. 剩余的股票采取年报的其他股票
3. 如果前十的比例已经相较于年报发生变化，那么根据变化的比例对剩余股票进行比例增减持
'''
for k, v in first_top_10:
    if k in year_stock:
        del year_stock[k]

total = sum(float(v['percent']) for _, v in first_top_10)
last_remain_total = sum(float(v['percent']) for _, v in year_stock.items())
larger = last_remain_total - (stock_percent - total)

now_stock = {k: v for k, v in first_top_10}
for k, v in year_stock.items():
    v['percent'] -= v['percent']/last_remain_total * larger
    now_stock[k] = v


stock = 23749599191.28
bond = 1364435355.28
cash = 1956071813.28
other = 96394759.28
total = 27166501119.12


last_nav = fund_nav_dict['20210331']
begin = datetime.date(2021, 4, 1)
end = datetime.date(2021, 5, 28)
offset = 0
index = 1
for i in range((end - begin).days+1):
    today = (begin + datetime.timedelta(days=i)).strftime('%Y%m%d')
    yesterday = (begin + datetime.timedelta(days=i-1)).strftime('%Y%m%d')
    if today not in fund_nav_dict:
        continue
    data = engine.execute(f"select ts_code, close, pre_close from history where trade_date={today}")
    stock_now_percent = 0
    for item in data:
        code, price, pre_close = item
        diff = price / pre_close
        stock_now_percent += now_stock[code[:-3]]['percent'] * diff
        amount = now_stock[code[:-3]]['amount']
        now_stock[code[:-3]]['amount'] = float(''.join(str(amount).split(','))) * diff
    now_stock_amount = stock * stock_now_percent/stock_percent
    today_nav = last_nav * (now_stock_amount + bond + cash + other) / total

    real_today_nav = fund_nav_dict[today]
    print(today, "真实净值", real_today_nav, "估指: ", today_nav, "差值: ", round(real_today_nav-today_nav, 6),
          "差值比例: ", round(((real_today_nav-today_nav)/today_nav + offset/index) * 100, 5), "%")
    offset += (real_today_nav-today_nav)/today_nav
    last_nav = real_today_nav
    index += 1
    now_total = sum([dct['amount'] for code, dct in now_stock.items()])
    for code, dct in now_stock.items():
        now_stock[code]['percent'] = now_stock[code]['amount'] / now_total * stock_percent

print(index)

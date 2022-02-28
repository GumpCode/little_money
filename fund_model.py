#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/9 10:12 上午
# @Author  : ganlinhao

import os
import json
import pdfplumber
import tushare

year_stock_path = "data/163406/year_stock_163406.json"
year_bond_path = "data/163406/year_bond_163406.json"
year_pdf_path = "data/2020-12.pdf"

first_stock_path = "data/163406/first_stock_163406.json"
first_bond_path = "data/163406/first_bond_163406.json"
first_pdf_path = "data/2021-03.pdf"


'''
1. 获取全部股票的前一天收盘价和今天收盘价，取20210401到当天
2. 根据涨跌预测净值
3. 爬取基金对应的每天净值
'''

pro = tushare.pro_api('a1b1980392e6299231d1e3b8af1d0c943e536558f2f32bfd5a69ef2d')
#data = pro.query("daily", ts_code='000001.SZ', start_date="20210101", end_date="20210110")
#print(data)


if not os.path.exists(year_stock_path) and not os.path.exists(year_bond_path):
    year_stock = {}
    year_bond = {}
    with pdfplumber.open(year_pdf_path) as pdf:
        page = pdf.pages[54]
        for index, item in enumerate(page.extract_tables()[-1]):
            if index <= 3:
                continue
            year_stock[item[1]] = {
                "index": item[0],
                "name": item[2],
                "amount": float(item[4].replace(',', "")),
            }

        for num in [55, 56]:
            page = pdf.pages[num]
            for item in page.extract_table():
                year_stock[item[1]] = {
                    "index": item[0],
                    "name": item[2],
                    "amount": float(item[4].replace(',', "")),
                }

        page = pdf.pages[57]
        for index, item in enumerate(page.extract_tables()[0]):
            year_stock[item[1]] = {
                "index": item[0],
                "name": item[2],
                "amount": float(item[4].replace(',', "")),
            }

        page = pdf.pages[60]
        for index, item in enumerate(page.extract_tables()[0]):
            if index < 2:
                continue
            year_bond[item[1]] = {
                "index": item[0],
                "name": item[2],
                "amount": float(item[4].replace(',', "")),
            }

    total_amount = sum(v['amount'] for k, v in year_stock.items())
    for k, v in year_stock.items():
        data = tushare.get_realtime_quotes(k)
        year_stock[k]['price'] = float(data.loc[0]['price'])
        year_stock[k]['pre_close'] = float(data.loc[0]['pre_close'])
        year_stock[k]['percent'] = v['amount'] / total_amount

    with open(year_stock_path, 'w', encoding='utf8') as f:
        f.write(json.dumps(year_stock, ensure_ascii=False))

    with open(year_bond_path, 'w', encoding='utf8') as f:
        f.write(json.dumps(year_bond, ensure_ascii=False))


if not os.path.exists(first_stock_path) and not os.path.exists(first_bond_path):
    first_stock = {}
    first_bond = {}
    with pdfplumber.open(first_pdf_path) as pdf:
        page = pdf.pages[6]
        for index, item in enumerate(page.extract_tables()[-1]):
            if index <= 3:
                continue
            first_stock[item[1]] = {
                "index": item[0],
                "name": item[2],
                "amount": float(item[4].replace(',', "")),
            }

        page = pdf.pages[7]
        for item in page.extract_tables()[0]:
            first_stock[item[1]] = {
                "index": item[0],
                "name": item[2],
                "amount": float(item[4].replace(',', "")),
            }

        page = pdf.pages[7]
        for index, item in enumerate(page.extract_tables()[-1]):
            if index < 3:
                continue
            data = tushare.get_realtime_quotes(item[1])
            first_bond[item[1]] = {
                "index": item[0],
                "name": item[2],
                "amount": float(item[4].replace(',', "")),
            }

    total_amount = 23749599191.28
    #for k, v in first_bond.items():
    #    data = tushare.get_realtime_quotes(k)
    #    first_bond[k]['price'] = float(data.loc[0]['price'])
    #    first_bond[k]['pre_close'] = float(data.loc[0]['pre_close'])
    #    first_bond[k]['percent'] = v['amount'] / total_amount

    for k, v in first_stock.items():
        data = tushare.get_realtime_quotes(k)
        first_stock[k]['price'] = float(data.loc[0]['price'])
        first_stock[k]['pre_close'] = float(data.loc[0]['pre_close'])
        first_stock[k]['percent'] = v['amount'] / total_amount

    with open(first_stock_path, 'w', encoding='utf8') as f:
        f.write(json.dumps(first_stock, ensure_ascii=False))

    with open(first_bond_path, 'w', encoding='utf8') as f:
        f.write(json.dumps(first_bond, ensure_ascii=False))


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
last_worth = 2.0912
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

stock_now_percent = 0
for k, v in now_stock.items():
    diff = v['price'] / v['pre_close']
    print(k, v['price'], v['pre_close'])
    stock_now_percent += v['percent'] * diff

#bond_now_percent = 0
#for k, v in first_bond.items():
#    diff = v['price'] / v['pre_close']
#    bond_now_percent += v['percent'] * diff

stock = 23749599191.28
bond = 1364435355.28
cash = 1956071813.28
other = 96394759.28
total = 27166501119.12

print(stock + bond + cash + other)
print(stock / total)

now_stock = stock * stock_now_percent/stock_percent
print(now_stock)
print(last_worth * (now_stock + bond + cash + other) / total)

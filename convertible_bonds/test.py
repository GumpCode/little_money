#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 10:32 下午
# @Author  : ganlinhao

# 导入tushare
import tushare as ts
import datetime
import numpy as np

# 初始化pro接口
pro = ts.pro_api('a1b1980392e6299231d1e3b8af1d0c943e536558f2f32bfd5a69ef2d')

# 拉取数据
df = pro.cb_basic(**{
    "ts_code": "",
    "list_date": "",
    "exchange": "",
    "limit": "",
    "offset": ""
}, fields=[
    "ts_code",
    "bond_short_name",
    "cb_code",
    "stk_code",
    "stk_short_name",
    "maturity",
    "issue_size",
    "remain_size",
    "maturity_date",
    "list_date",
    "delist_date",
    "conv_start_date",
    "first_conv_price",
    "conv_price",
    "value_date",
    "newest_rating"
])

#checkinDate = datetime.datetime.today().date() - datetime.timedelta(days=3)
checkinDate = datetime.date.today()
checkin_date = checkinDate.strftime("%Y%m%d")
checkin_date_ = checkinDate.strftime("%Y-%m-%d")
selected_bond = {}
stk2bond = {}
for row in df.iterrows():
    delist_date = row[1]["delist_date"]
    remain_size = row[1]["remain_size"]
    if row[1]["delist_date"]:  # 强赎的排除掉
        continue
    if row[1]["list_date"] and row[1]["list_date"] > checkin_date_:  # 未上市的排除掉
        continue
    if float(remain_size) > 5e8:  # 小于伍亿元的排除掉
        continue
    selected_bond[row[1]["ts_code"]] = row[1]
    stk2bond[row[1]["stk_code"]] = row[1]["ts_code"]


def get_premium_rate(bonds):
    stk_df = pro.daily(**{
        "ts_code": ",".join([item["stk_code"] for item in bonds.values()]),
        "trade_date": checkin_date,
    }, fields=["ts_code", "close", "trade_date"])
    for row in stk_df.iterrows():
        stk_close_price = row[1]["close"]
        stk_code = row[1]["ts_code"]
        bond_code = stk2bond[stk_code]
        conv_price = bonds[bond_code]["conv_price"]
        bond_close_price = bonds[bond_code]["close"]
        conv_value = stk_close_price/conv_price * 100
        premium_rate = bond_close_price/conv_value - 1
        bonds[bond_code]["premium_rate"] = premium_rate
    return bonds


def get_bond_close_price(bonds):
    prices = pro.cb_daily(**{
        "trade_date": checkin_date,
    }, fields=["ts_code", "close", "trade_date"])
    prices_dct = {}
    for p in prices.iterrows():
        code, close = p[1]["ts_code"], p[1]["close"]
        prices_dct[code] = close
    new_bonds = {}
    for code, obj in bonds.items():
        if code not in prices_dct:
            price = pro.cb_daily(**{
                "ts_code": code,
                "trade_date": checkin_date,
            }, fields=["ts_code", "close", "trade_date"])
            if not price.empty:
                prices_dct[code]["close"] = price["close"]
        try:
            obj["close"] = prices_dct[code]
        except Exception:
            continue
        new_bonds[code] = obj
    return new_bonds


selected_bond = get_bond_close_price(selected_bond)
selected_bond = get_premium_rate(selected_bond)

price_threshold = 180
premium_rate_threshold = 1
remain_size_threshold = 10e8
selected_bond = [bond for bond in selected_bond.values()
                 if bond["close"] <= price_threshold and
                 bond["remain_size"] < remain_size_threshold and
                 bond["premium_rate"] < premium_rate_threshold]
close_mean = np.mean([v["close"] for v in selected_bond])
close_std = np.std([v["close"] for v in selected_bond])
close_max = np.max([v["close"] for v in selected_bond])
close_min = np.min([v["close"] for v in selected_bond])
remain_mean = np.mean([v["remain_size"] for v in selected_bond])
remain_std = np.std([v["remain_size"] for v in selected_bond])
remain_max = np.max([v["remain_size"] for v in selected_bond])
remain_min = np.min([v["remain_size"] for v in selected_bond])
premium_mean = np.mean([v["premium_rate"] for v in selected_bond])
premium_std = np.std([v["premium_rate"] for v in selected_bond])
premium_max = np.max([v["premium_rate"] for v in selected_bond])
premium_min = np.min([v["premium_rate"] for v in selected_bond])


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


def metrics(bond):
    close_value = (bond["close"] - close_min)/(close_max - close_min)
    rate_value = (bond["premium_rate"] - premium_min)/(premium_max - premium_min) * sigmoid(close_value * 10)
    size_value = (bond["remain_size"] - remain_min)/(remain_max - remain_min)
    if bond["close"] > 130:
        rate_value += 1
    value = close_value + rate_value + size_value
    if bond["ts_code"].startswith("123") or bond["ts_code"].startswith("128"):
        value *= 0.9
    return value


selected_bond = sorted(selected_bond, key=lambda x: metrics(x))
for num, bond in enumerate(selected_bond[:20]):
    print(num+1, bond["ts_code"], bond["bond_short_name"], bond["close"], bond["premium_rate"], bond["remain_size"], metrics(bond))


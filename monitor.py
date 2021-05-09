#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/11 9:38 下午
# @Author  : ganlinhao

import schedule
from fund_sprider import JslFund, EastMoneyFund
from wechat_notice import push_to_wechat
from utils import today_is_tradeday, between_special_time


active_fund = {
    "163417": "兴全合宜",
    "163402": "兴全趋势",
    "163415": "兴全模式",
    "162605": "景顺鼎益",
    "161005": "富国天惠",
    "161903": "万家优选",
    "162703": "广发小盘"
}

etf_fund = {
    "501057": "新能源车",
    "165525": "基建工程",
    "501058": "新能车C",
    "501090": "消费龙头",
    "502056": "医疗基金"
}


is_final = False


def get_and_push_data(start, end):
    if not between_special_time(start, end):
        return

    jsl = JslFund(active_fund, etf_fund)
    east_money = EastMoneyFund(active_fund, etf_fund)
    all_fund = {**active_fund, **etf_fund}

    threshold = 0.5
    res = []
    if jsl.get_activate_data() and jsl.get_etf_data() and east_money.get_all_data():
        jsl_data = {**jsl.active_fund_data, **jsl.etf_fund_data}
        east_money_data = {**east_money.active_fund_data, **east_money.etf_fund_data}
        for _id, name in all_fund.items():
            if _id in jsl_data and _id in east_money_data:
                price = float(jsl_data[_id]["price"])
                jsl_rt = float(jsl_data[_id]["discount_rt"])
                east_money_rt = 1 - float(east_money_data[_id]["estimate_value"]) / price
                if jsl_rt > threshold or east_money_rt > threshold:
                    res.append({
                        "id": _id,
                        "name": all_fund[_id],
                        "rate": {
                            "jsl": jsl_rt,
                            "east_money": round(east_money_rt * 100, 2)
                        }
                    })

        if res:
            push_to_wechat(res)


if __name__ == '__main__':
    schedule.every(20).minutes.do(get_and_push_data, start="09:40", end="11:40")
    schedule.every(15).minutes.do(get_and_push_data, start="13:00", end="15:10")
    schedule.every(15).minutes.do(get_and_push_final_data, start="18:00", end="23:00")

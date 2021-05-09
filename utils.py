#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/30 3:47 下午
# @Author  : ganlinhao


import urllib.request as request
import datetime

'''
@query a single date: string '20170401';
@api return day_type: 0 workday 1 weekend 2 holiday -1 err
@function return day_type: 1 workday 0 weekend&holiday
'''


def get_day_type(query_date):
    url = 'http://tool.bitefu.net/jiari/?d=' + query_date
    resp = request.urlopen(url)
    content = resp.read()
    if content:
        try:
            day_type = int(content)
        except ValueError:
            return -1
        else:
            return day_type
    else:
        return -1


def is_tradeday(query_date):
    weekday = datetime.datetime.strptime(query_date, '%Y%m%d').isoweekday()
    if weekday <= 5 and get_day_type(query_date) == 0:
        return 1
    else:
        return 0


def today_is_tradeday():
    query_date = datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')
    return is_tradeday(query_date)


def between_special_time(start, end):
    start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + start, '%Y-%m-%d%H:%M')
    end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + end, '%Y-%m-%d%H:%M')
    # 当前时间
    now_time = datetime.datetime.now()
    # 判断当前时间是否在范围时间内
    return start_time <= now_time <= end_time


if __name__ == '__main__':
    print(is_tradeday('20210129'))
    print(today_is_tradeday())

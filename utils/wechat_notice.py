#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/30 3:28 下午
# @Author  : ganlinhao

import requests


server_keys = [
    "SCU74536Ta1e32f80805fc5c329fdaf45652997775e0acf6fca47c"
]


def push_to_wechat(text, desp):
    data = {
        "text": text,
        "desp": desp
    }
    for key in server_keys:
        url = f"https://sc.ftqq.com/{key}.send?text="
        requests.post(url, data=data)

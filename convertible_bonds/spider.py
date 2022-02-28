#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 10:03 下午
# @Author  : ganlinhao

import pprint
import requests

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,br', 'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8',
    'Cache-Control': 'no-cache', 'Connection': 'keep-alive',
    'Host': 'www.jisilu.cn', 'Pragma': 'no-cache', 'Referer': 'https://www.jisilu.cn/',
    'Upgrade-Insecure-Requests': '1',
    "Cookie": "kbzw__Session=5sgbf9g3psfkkhksom6dvja4c6; Hm_lvt_164fe01b1433a19b507595a43bf58262=1628347502; kbz_newcookie=1; kbzw_r_uname=Gumpglh; Hm_lpvt_164fe01b1433a19b507595a43bf58262=1628434825; kbzw__user_login=7Obd08_P1ebax9aXvtfj0d7j25mcndHV7Ojg6N7bwNOMqdqkqcOnwtatq56yzd3EqZTdqqfcxamTpNqmn66l3cWXnKTs3Ny_zYynrqqeqZyYnaO2uNXQo67f293l4cqooaWSlonE2Nbhz-TQ5-GwicLa68figcTY1piww4HMmaaZ2J2rwayKl7jj6M3VuNnbwNLtm6yVrY-qrZOgrLi1wcWhieXV4seWqNza3ueKkKTc6-TW3puwkqSRpaunq5Gek6Wrlbza0tjU35CsqqqmlKY",
    'User-Agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/67.0.3396.99Safari/537.36'
}

url = "https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t=1628437288593"
data = {
    "bond_ids": "",
    "btype": "",
    "curr_iss_amt": "",
    "fprice": "",
    "industry": None,
    "is_search": "N",
    "listed": "Y",
    "market_cd": ["shmb","shkc","szmb","szcy"],
    "page": 1,
    "premium_rt": "",
    "qflag": "N",
    "rating_cd": "",
    "rp": 50,
    "svolume": "",
    "sw_cd": "",
    "tprice": "",
    "volume": "",
    "ytm_rt": ""
}
res = requests.post(url=url, headers=headers, data=data)
pprint.pprint(res.json())
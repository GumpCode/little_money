#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/29 3:16 下午
# @Author  : ganlinhao


import json
from flask import request,Flask

server = Flask(__name__)  # 创建一个服务，把当前这个python文件当做一个服务


@server.route('/data/get',methods=['get'])
def data():  # 返回data
    data = {
        'User': {
            'id': '66',
            'name': '李华'
        }
    }
    return data

@server.route('/data/post', methods=['post'])
def data_post():
    r = request.data
    da=json.loads(r)
    print(da)
    return da


if __name__ == '__main__':
    server.run(host='0.0.0.0',port=1360,debug=True)  # 指定访问端口、host

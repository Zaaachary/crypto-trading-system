# -*- encoding: utf-8 -*-
'''
@File    :   account_data.py
@Time    :   2024/04/21 20:48:16
@Author  :   Zhifeng Li
@Contact :   li_zaaachary@outlook.com
@Desc    :   定时获取账户金额，并保存至 excel。
https://www.okx.com/docs-v5/zh/?python#trading-account-rest-api-get-balance
https://github.com/pyted/okx/tree/master
pip install okx
'''

import os
import time
from typing import List
import datetime
from copy import deepcopy
from collections import defaultdict

import pandas as pd
from okx.api import Account

def parse_balance(balance_response: dict):
    data = balance_response['data'][0]
    dt_object = datetime.datetime.fromtimestamp(int(data['uTime'])/1000)
    formatted_string = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    result = {
        'market_flag': 'real' if balance_response['code'] == '0' else 'unreal',
        'totalEq': data['totalEq'],
        'detail': {},
        'datetime': formatted_string,
        'timestamp': formatted_string
    }
    
    detail_map = {}
    for item in data['details']:
        coin_name = item['ccy']
        coin_eq = item['eq']
        coin_useq = float(item['disEq'])
        if coin_useq < 1:
            continue
        result['detail'][coin_name] = {'eq': float(coin_eq), 'usd_eq': float(coin_useq)}
        detail_map[coin_name] = item

    coin_list = sorted(list(result['detail'].keys()), key=lambda x:result['detail'][x]['usd_eq'], reverse=True)
    for coin_name in coin_list:
        print(coin_name, round(result['detail'][coin_name]['usd_eq'], 2))
    return result

def save_result(result: List[dict]):
    data = {'时间': [], '总额': []}

    coin_set = set()
    for item in result:
        coin_set.update(item['detail'].keys())

    data.update({key: [] for key in coin_set})
    
    for item in result:
        data['时间'].append(item['datetime'])
        data['总额'].append(round(float(item['totalEq']),2))
        notexits_coin = deepcopy(coin_set)
        for coin, detail in item['detail'].items():
            notexits_coin.remove(coin)
            data[coin].append(round(detail['usd_eq'], 2))
    
    df = pd.DataFrame(data)
    fixed_columns = ['时间', '总额']
    import pdb; pdb.set_trace()
    last_row_sorted = df.iloc[-1, 2:].sort_values(ascending=False)
    sorted_columns = last_row_sorted.index.tolist()
    sorted_columns = fixed_columns + sorted_columns
    df = df.reindex(columns=sorted_columns)
    df.to_excel('coin_value_total.xlsx', index=False)


if __name__ == "__main__":

    api_key = os.environ['okx_api_key']
    secret_key = os.environ['okx_secret_key']
    passphrase = os.environ['okx_passphrase']
    flag = '0'  # 实盘：0；虚拟盘：1

    proxies = {
        'http': '127.0.0.1:1087',
        'https': '127.0.0.1:1087',
    }
    proxy_host = None

    account = Account(key=api_key, secret=secret_key, passphrase=passphrase, flag=flag, proxies=proxies, proxy_host=proxy_host)

    result_list = []

    while True:
        time.sleep(300)
        result1 = account.get_balance()  # 查看账户余额
        result = parse_balance(result1)
        result_list.append(result)
        save_result(result_list)


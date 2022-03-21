import requests
import UAS
import json
import jsonpath
import re
import pandas as pd
import emoji
import numpy as np
from tkinter import messagebox
import tkinter as tk


def create_response(url):
    headers = UAS.get()
    response = requests.get(url=url, headers=headers)
    response.encoding = 'utf-8'
    return response


def get_oid(response):
    content = response.text
    # 获取aid,用于后续地址的oid
    aid = re.findall('{\"aid\":(.*?),', content)[0]
    return aid


def remove_emoji(text):
    new_text = []
    for item in text:
        # 数据清洗真的是一辈子的事情
        # 去除表情
        temp = re.sub('\[.*?\]', '', item)
        temp = emoji.demojize(temp)
        temp = re.sub(':.*?:', '', temp)
        # 去除@用户的回复 字段
        temp = re.sub('回复 @(.*?) :', '', temp)
        # 去除网址, 不知道为什么有些网址去除不掉，小瑕疵……能力有限
        temp = re.sub('http:.*', '', temp)
        temp = re.sub('https:.*\b', '', temp)
        # 去除BV号
        temp = re.sub('BV.*\b', '', temp)
        new_text.append(temp)
    return new_text


def get_data(oid, end_page):
    data = pd.DataFrame(index=['name', 'text', 'like_counts']).T
    for item in range(end_page):
        # 拼接 url
        url = "https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={page}&type=1&oid={oid}&mode=3&plat=1".format(
            page=str(item + 1), oid=oid)
        # 请求网页
        response = create_response(url)
        # 获取json数据
        content = response.text
        obj = json.loads(content)
        text = jsonpath.jsonpath(obj, '$...message')
        del text[0]
        # 去除表情,@回复,进行数据清洗
        text = remove_emoji(text)
        like_counts = jsonpath.jsonpath(obj, '$..replies[*].like')
        name = jsonpath.jsonpath(obj, '$..replies[*].member.uname')
        info = pd.DataFrame([name, text, like_counts],
                            index=['name', 'text', 'like_counts']).T
        data = data.append(info, ignore_index=True)
    return data


def write_data(data):
    data.to_excel('.\data\Bilibili_comment.xlsx')


if __name__ == '__main__':
    # 评论默认以热度排序
    # 默认从第一页开始，输入结束页数
    BV = 'BV13S4y1g7iq'
    ori_url = 'https://www.bilibili.com/video/' + BV
    end_page = int(input('请输入页数:'))
    response = create_response(ori_url)
    oid = get_oid(response)
    data = get_data(oid, end_page)
    data = data.replace(to_replace='', value='None')
    data = data.replace(to_replace='None', value=np.nan).dropna()
    # 获取数据后写入excel文档
    write_data(data)
"""
To Do:
    可视化界面
    数据清洗精细化
"""
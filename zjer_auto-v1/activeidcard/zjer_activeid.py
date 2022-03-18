#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 创建日期: 2018/5/29
# www.zjer.cn 之江汇教育自动登录工具

__author__ = 'kylinpoet'

import requests
import time
import json
import urllib.parse
from colorama import Fore, init
import xlrd

init(autoreset=True)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'Referer': 'http://yun.zjer.cn/index.php',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
__try_time = 3
__time_out = 10


def print_time_line(pref=''):
    print(f"{Fore.CYAN}{pref}#-------------{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}------------->")


def time_log() -> str:
    return "  ###  " + \
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + "  ###"


def try_log(retry_state):
    """return the result of the last call attempt"""
    print(f'重试第：{retry_state.attempt_number}次.')


t_urls_info: list = []
user_Data_all: list = []


def read_user_data(filename='teacher_info.txt') -> list:
    """
    :param filename:
    :return: a list of user info dict
    """
    global user_Data_all
    user_Data_all = []
    user_info_dict = {'class': '', 'name': '', 'id': '', 'pass': ''}

    user_data = xlrd.open_workbook(filename)
    user_table = user_data.sheet_by_index(0)
    user_rows = user_table.nrows

    global t_urls_info
    t_urls_info = []
    try:
        for i in range(1, user_rows):
            user_info_dict['class'] = user_table.row_values(i)[0]
            user_info_dict['name'] = user_table.row_values(i)[1]
            user_info_dict['id'] = user_table.row_values(i)[2]
            user_info_dict['pass'] = user_table.row_values(i)[3]
            user_Data_all.append(user_info_dict.copy())
            user_info_dict = {
                'class': '', 'name': '', 'id': '', 'pass': ''}
    except Exception as e:
        print(Fore.RED + '读取账号信息失败，错误提示为：' + str(e))
    return user_Data_all


class MyException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):  # 这里就是异常的字符串信息
        return self.message


def user_login(
        userid='',
        userpass='',
        user_order=0,
        user_amount=0,
        try_time=__try_time):
    i = 1
    for i in range(1, try_time + 1):
        try:
            req_session = requests.Session()
            login_url = 'http://yun.zjer.cn/index.php?r=portal/user/doLoginPortal&ajax=1&callback=jQuery17209088366810393329_1510879853036&userId={}&userPsw={}'
            response = req_session.get(
                login_url.format(
                    userid,
                    urllib.parse.quote(userpass)),
                headers=headers,
                timeout=__time_out)

            login_user_info = {
                'session': '',
                'userinfo': '',
                'order': 0,
                'order_amount': 0}

            response_json = json.loads(
                response.text[response.text.find('(') + 1:-1])

            resp_code = response_json.get('code')
            if resp_code == '000000':

                user_name = response_json['userinfo']['name']
                # print(user_name + "login ok!", time_log())
                print(f"{Fore.GREEN}{user_name:{chr(12288)}<5}登陆成功.    {time_log()}")

                # 获取分类
                login_user_info['session'] = req_session
                login_user_info['userinfo'] = response_json['userinfo']
                login_user_info['order'] = user_order
                login_user_info['order_amount'] = user_amount

                return login_user_info
            else:
                print_time_line()
                print(userid, response_json.get('message'))
                if '密码错误' not in response_json.get('message'):
                    raise MyException('网站自报登录异常')
                else:
                    return {}
        except Exception as e:
            print_time_line()
            print(f'{Fore.RED}{userid}登录失败，错误提示为:{e}')
            if i <= try_time:
                print(f'{Fore.CYAN}重试第{i}次...')
            else:
                return {}


def active_id(login_user_info, name='', account='', default_pass='ow2019'):
    i = 1
    for i in range(1, __try_time + 1):
        try:
            url_active = 'http://yun.zjer.cn/index.php?r=center/person/Activate/ActivateIDCard'
            payload = 'account={0}&password={1}&IDCard={2}&name={3}&email='
            payload = payload.format(
                account,
                default_pass,
                account,
                urllib.parse.quote(name))
            response = login_user_info['session'].post(
                url_active,
                data=payload,
                headers=headers,
                timeout=__time_out)
            pass

            if '000000' in response.text:
                print(Fore.GREEN + name + ' 激活成功!')
                return 1
            else:
                resp_json = response.json()
                print(
                    Fore.RED +
                    name +
                    ' 激活失败!' +
                    resp_json.get(
                        'content',
                        '未知错误'))
                return 0
        except Exception as e:
            print(Fore.RED + name + ' 激活失败,错误为：' + str(e))
            if i <= __try_time:
                print(f'{Fore.CYAN}重试第{i}次...')
            else:
                return 0


if __name__ == '__main__':
    print(Fore.CYAN + "zj_zuto 正在启动...    " + time_log())
    identify_path = 'name.xls'
    read_user_data(identify_path)
    len_identify_account = len(user_Data_all)
    for user_order, user_info in enumerate(user_Data_all):

        user_login_info = user_login(user_info['id'],
                                     user_info['pass'],
                                     user_order + 1,
                                     len_identify_account)

        time.sleep(0.5)
        if user_login_info:
            print(
                f"正在处理:{user_order+1}/{len_identify_account}  {user_info['class']}{user_info['name']}")
            ret = active_id(
                user_login_info,
                user_info['name'],
                user_info['id'])

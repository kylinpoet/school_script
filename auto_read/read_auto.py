#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 创建日期: 2019-11-20 13:44:02
# yuntu.wzer.net 阅读量

__author__ = 'kylinpoet'

import requests
import time
import json
import urllib.parse
from colorama import Fore, init
import xlrd
import re
from tenacity import *
import random

init(autoreset=True)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'Referer': 'http://yuntu.wzer.net',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
__try_time = 3
__time_out = 10


def try_log(retry_state):
    """return the result of the last call attempt"""
    print(f'重试第：{retry_state.attempt_number}次.')


class MyException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):  # 这里就是异常的字符串信息
        return self.message


def print_time_line(pref=''):
    print(f"{Fore.CYAN}{pref}#-----------{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}----------->")


def time_log() -> str:
    return "  ###  " + \
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + "  ###"


def user_login(
        user_id='',
        user_pass='',
        user_name='',
        try_time=__try_time):
    i = 1
    schoolCode = ''
    for i in range(1, try_time + 1):
        try:
            req_session = requests.Session()
            url_doLoginBarcode = 'http://yuntu.wzer.net/doLoginBarcode?loginName={}&password={}&autologin=on'
            response = req_session.get(
                url_doLoginBarcode.format(
                    urllib.parse.quote(user_id),
                    urllib.parse.quote(user_pass)),
                headers=headers,
                timeout=__time_out)
            resp_json = response.json()
            if not resp_json.get('success'):
                print(f'{Fore.RED}用户名或密码错误')
                return {}
            else:
                same_user = resp_json.get('data', {}).get('listReader', [])
                len_same_user = len(same_user)
                if len_same_user > 0:
                    for j in range(len_same_user):
                        if user_name == same_user[j].get('name', ''):
                            schoolCode = same_user[j].get('schoolCode', '')
                            break
                    if schoolCode == '':
                        print(f'{Fore.RED}找不到学校ID')
                        return {}
                    login_url = 'http://yuntu.wzer.net/doLoginBarcodeConfirm?schoolCode={}&loginName={}&password={}'
                    response = req_session.get(
                        login_url.format(
                            schoolCode,
                            urllib.parse.quote(user_id),
                            urllib.parse.quote(user_pass)),
                        headers=headers,
                        timeout=__time_out)
                    if '欢迎您' in response.text:
                        print(f"{Fore.GREEN}{user_id} {user_name:{chr(12288)}<4} 登陆成功.    {time_log()}")
                        return req_session
                    else:
                        print('用户名或密码错误')
                        return {}
                # 如果没有重名，表示直接登录成功，不需要选择区域
                else:
                    print(f"{Fore.GREEN}{user_id} {user_name:{chr(12288)}<4} 登陆成功.    {time_log()}")
                    return req_session
        except Exception as e:
            print_time_line()
            print(f'{Fore.RED}{user_id}登录失败，错误提示为:{e}')
            if i <= try_time:
                print(f'{Fore.CYAN}重试第{i}次...')
            else:
                return {}

# 连环画 中华成语典故
# 'http://218.75.16.90:8080/ReadRoom/aazhcydg/list.html?libcode='


@retry(
    retry=retry_if_exception_type(),
    stop=stop_after_attempt(3),
    after=try_log,
    wait=wait_exponential(multiplier=1, min=2, max=10))
def get_book(login_user_session,
             category_id=15,
             all_counts=2,
             ) -> tuple:
    """
    # y_l_s 固定保存在 http://218.75.16.90:8080/ReadRoom/aazhcydg/js/data.js
    """
    url_get_book = 'http://218.75.16.90:8080/ReadRoom/handler/Helper.ashx/C_G_B'
    # c是分类,p是页数 s是书籍数
    payload = f'c={category_id}&p={random.randint(1,860//all_counts)}&s={all_counts}'  # 860
    response = login_user_session.post(
        url_get_book,
        data=payload,
        headers=headers,
        timeout=__time_out)
    book_info = response.json()
    if book_info.get(
        'isSuccess',
        False) and book_info.get(
        'error',
            'error') == '':
        book_result = tuple(book_info.get('result'))
        return book_result
    else:
        print(f'{Fore.RED}获取图书目录失败')
        return ()


def log_book(
        login_user_session,
        book_result: tuple,
        user_info: dict,
        libcode='4A251A41DD7BA98230DBD37E0496CAD5ED4DC77D771C1F7072DDCF1CBE32F89B1C9EE95BF762DFD9',
        y_l_s='1BD11563E1AD8E2D08EA724ED18752AFAE2BE045B0E387F7'):
    for i, book in enumerate(book_result):
        sleep(random.randint(3, 5))
        book_m = book.get('m')  # 5251
        book_p = book.get('p')  # 06E0D310AFD1C7A91CF252CF5A925184
        book_name = book.get('bookname')
        _url = 'http://218.75.16.90:8080/ReadRoom/Reader/ReadBook.aspx?'
        _url = _url + f'libcode={libcode}&m={book_m}&p={book_p}&y_l_s={y_l_s}'
        _c = ''
        try:
            response = login_user_session.get(
                _url,
                headers=headers,
                timeout=__time_out)
            _return = response.text
            regex = re.compile(r'reader001/Main.aspx\?m=(.+?)&amp', )
            _c = regex.findall(response.text)[0]
            _c = _c + '%7C' + y_l_s
        except Exception as e:
            print(f'{Fore.RED}{book_name}图书验证失败，错误代码:{e}')
        url_log = 'http://218.75.16.90:8080/ReadRoom/handler/Log.ashx/log'
        payload = f'libcode={libcode}&a=4&b=1&c={_c}'
        try:
            response = login_user_session.post(
                url_log,
                data=payload,
                headers=headers,
                timeout=__time_out)
            print(
                f"{Fore.GREEN}{user_info.get('user_id')} {user_info.get('user_name')} 阅读{book_name}成功")
        except Exception as e:
            print(f'{Fore.RED}{book_name}读书阅读失败，错误代码:{e}')
    return 1


@retry(
    retry=retry_if_exception_type(),
    stop=stop_after_attempt(3),
    after=try_log,
    wait=wait_exponential(multiplier=1, min=2, max=10))
def get_session(login_user_session):
    _cookies = requests.utils.dict_from_cookiejar(login_user_session.cookies)
    # 将字典转为CookieJar：
    # cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
    sessToken = _cookies.get('sessToken')
    _url = f'http://218.75.16.90:8080/?token={sessToken}'
    response = login_user_session.get(
        _url,
        headers=headers,
        timeout=__time_out)
    return login_user_session


def read_user_data(filename='name.xls',
                   default_pass='123456') -> tuple:

    _user_data_all = []
    user_info_dict = {'user_class': '',
                      'user_id': '',
                      'user_name': '',
                      'user_pass': ''}

    user_data = xlrd.open_workbook(filename)
    user_table = user_data.sheet_by_index(0)
    user_rows = user_table.nrows
    try:
        for i in range(1, user_rows):
            user_info_dict['user_class'] = user_table.row_values(i)[1]
            user_info_dict['user_id'] = user_table.row_values(i)[2]
            user_info_dict['user_name'] = user_table.row_values(i)[3]
            user_info_dict['user_pass'] = default_pass

            _user_data_all.append(user_info_dict.copy())
            user_info_dict = {'user_class': '',
                              'user_id': '',
                              'user_name': '',
                              'user_pass': ''}
        return tuple(_user_data_all)
    except Exception as e:
        print(Fore.RED + '读取账号信息失败，错误提示为：' + str(e))
        return ()


import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = ''
    parser.add_argument('-f', "--filename", help="账号文件名", type=str)
    parser.add_argument("-p", "--userpass", help="默认密码", type=str)
    parser.add_argument("-m", "--readamount", help="默认读书量", type=int)
    args = parser.parse_args()
    filename = args.filename if args.filename else '学校读者清单.xls'
    userpass = args.userpass if args.userpass else '123456'
    readamount = args.readamount if args.readamount else 2

    user_data = read_user_data(filename, userpass)
    if user_data:
        user_info = user_data[0]
        user_session = user_login(user_info.get('user_id'), user_info.get('user_pass'), user_info.get('user_name'))
        __book_result = ()
        try:
            __book_result = get_book(user_session, all_counts=readamount)
        except Exception as e:
            print(f'{Fore.RED}获取图书目录失败,{e}')

    # 以下循环登录
    if __book_result:
        # user_data = read_user_data(filename, userpass)
        for index, user_info in enumerate(user_data):
            user_session = user_login(
                user_info.get('user_id'),
                user_info.get('user_pass'),
                user_info.get('user_name'))
            if user_session:
                __book_result = ()
                try:
                    __book_result = get_book(user_session, all_counts=readamount)
                except Exception as e:
                    print(f'{Fore.RED}{user_info.get("user_name")}获取图书目录失败,{e}')
                if __book_result:
                    try:
                        token_session = get_session(user_session)
                        log_book(token_session, __book_result, user_info)
                    except Exception as e:
                        print(f'{Fore.RED}{user_info.get("user_name")}访问相应网站错误，{e}')

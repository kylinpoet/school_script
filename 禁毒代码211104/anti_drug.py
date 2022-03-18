#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 创建日期: 2018/5/29
# www.zjer.cn 2-class禁毒

__author__ = 'kylinpoet'

import requests
import time
import json
import urllib.parse
from colorama import Fore, init
import xlrd
import re
import random

import ssl

ssl._create_default_https_context = ssl._create_unverified_context #创建默认不认证的https文本
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


init(autoreset=True)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'Referer': 'https://www.2-class.com',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

headers_json = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'Referer': 'https://www.2-class.com',
    'Content-Type': 'application/json; charset=UTF-8'}

__try_time = 3
__time_out = 20


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


def read_user_data(filename='student.xls') -> list:
    """
    :param filename:
    :return: a list of user info dict
    """
    global user_Data_all
    user_Data_all = []
    user_info_dict = {'account': '', 'pass': ''}

    user_data = xlrd.open_workbook(filename)
    user_table = user_data.sheet_by_index(0)
    user_rows = user_table.nrows

    global t_urls_info
    t_urls_info = []
    try:
        for i in range(1, user_rows):
            user_info_dict['account'] = user_table.row_values(i)[5]
            user_info_dict['pass'] = str(int(user_table.row_values(i)[6])) if (isinstance(user_table.row_values(i)[6],int) or isinstance(user_table.row_values(i)[6],float)) else user_table.row_values(i)[6]
            user_Data_all.append(user_info_dict.copy())
            user_info_dict = {
                'account': '', 'pass': ''}
    except Exception as e:
        print(Fore.RED + '读取账号信息失败，错误提示为：' + str(e))
    return user_Data_all


class MyException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):  # 这里就是异常的字符串信息
        return self.message

def get_reqtoken():
    _url = 'https://www.2-class.com/'
    req_session = requests.Session()
    req_session.headers.update(headers)
    for i in range(1, __try_time +1):
        try:
            response = req_session.get(
                _url,
                headers=headers,
                timeout=__time_out,
                verify=False)
            regex = re.compile('reqtoken:"(.+?)"')
            reqtoken1 = re.findall(regex, response.text)
            if reqtoken1:
                reqtoken = reqtoken1[0]
            return req_session, reqtoken
        except Exception as e:
            print(f'{Fore.RED}get_reqtoken函数失败')
            print(e)
            if i <= __try_time:
                print(f'{Fore.CYAN}重试第{i}次...')
            else:
                return None, None


def user_login(
        user_account='mazhanhu25',
        user_pass='wz123456',
        try_time=__try_time):
    i = 1
    req_session, reqtoken = get_reqtoken()
    if req_session and reqtoken:
        param = {"account": user_account,
                 "password": user_pass,
                 "checkCode": "",
                 "codeKey": "",
                 "reqtoken": reqtoken}
        _url = 'https://www.2-class.com/api/user/login'
        headers1 = headers.copy()
        headers1['Content-Type'] = 'application/json;charset=UTF-8'
        for i in range(1, try_time + 1):
            try:
                response = req_session.post(url=_url,
                                            headers=headers1,
                                            data=json.dumps(param),
                                            timeout=__time_out,
                                            verify=False)
                if response.json().get('success'):
                    return req_session, reqtoken
                else:
                    print(response.text)
                    return
            except Exception as e:
                print_time_line()
                print(f'{Fore.RED}{user_account}登录失败，错误提示为:{e}')
                if i <= try_time:
                    print(f'{Fore.CYAN}重试第{i}次...')
                else:
                    return


def quiz(req_session, reqtoken):
    exam_data = {"list": [
        {"questionId":2579,"questionContent":"D"},{"questionId":2580,"questionContent":"B"},
        {"questionId":2651,"questionContent":"A"},{"questionId":2588,"questionContent":"A"},
        {"questionId":2592,"questionContent":"C"},{"questionId":2657,"questionContent":"B"},
        {"questionId":2659,"questionContent":"A"},{"questionId":2661,"questionContent":"A"},
        {"questionId":2598,"questionContent":"C"},{"questionId":2601,"questionContent":"C"},
        {"questionId":2667,"questionContent":"B"},{"questionId":2668,"questionContent":"B"},
        {"questionId":2604,"questionContent":"B"},{"questionId":2605,"questionContent":"B"},
        {"questionId":2607,"questionContent":"D"},{"questionId":2671,"questionContent":"A"},
        {"questionId":2672,"questionContent":"A"},{"questionId":2608,"questionContent":"A"},
        {"questionId":2673,"questionContent":"A"},{"questionId":2610,"questionContent":"C"}],
                 "time": 216,
                 "reqtoken": reqtoken}
    # cookie_dict = {'m_h5_c': '29cfa96b2ce27a465fd693e8e9e16371_1575610515462%3B997ac3b6eb443e0503d9645463473b71',
    #                'sid': '49ef2ff1-9c37-43a3-a7ef-0688c7701862'}
    _url = 'https://www.2-class.com/api/quiz/commit'
    headers1 = headers.copy()
    headers1['Content-Type'] = 'application/json;charset=UTF-8'
    exam_data['reqtoken'] = reqtoken

    random.seed(time.time())
    list_num = list(range(20))
    random.shuffle(list_num)
    for n in list_num[0:4]:
        exam_data['list'][n]['questionContent'] = random.choice('ABCD')

    for i in range(1, __try_time + 1):
        try:
            response = req_session.post(url=_url,
                                        headers=headers1,
                                        data=json.dumps(exam_data),
                                        timeout=__time_out)
            dict_resp = response.json()
            if dict_resp.get('success'):
                try:
                    _url = 'https://www.2-class.com/api/quiz/getQuizCertificate'
                    response = req_session.get(_url, headers=headers, verify=False)
                    dict_resp = response.json()
                    print(f"{Fore.GREEN}{dict_resp['data']['userName']}{dict_resp['data']['point']}")
                    return
                except Exception as e :
                    print(Fore.RED + ' 返回成绩,错误为：' + str(e))
                return
            else:
                print(Fore.RED + ' 考试失败' + response.text)
                return
        except Exception as e:
            print(Fore.RED + ' 考试失败,错误为：' + str(e))
            if i <= __try_time:
                print(f'{Fore.CYAN}重试第{i}次...')
            else:
                return




def courseplay(req_session :requests.Session, reqtoken):
    _url ='https://2-class.com/api/course/getMycourseList?state=all&pageNo=1&pageSize=2'
    # headers1 = headers.copy();headers1['Content-Type'] = 'application/json;charset=UTF-8'
    # headers1['Content-Type'] = 'application/json;charset=UTF-8'
    # proxies = {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'}

    # 不知道为什么这里cookies的 sid 会丢失，所以要补一下
    cookie_dict = requests.utils.dict_from_cookiejar(req_session.cookies)
    cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
    req_session.cookies = cookies
    for i in range(1, __try_time +1):
        try:
            courselist = req_session.get(_url,verify=False).json()['data'].get('list')
            break
        except Exception as e:
            print(Fore.RED + ' 播放视频失败,错误为：' + str(e))
            if i <= __try_time:
                print(f'{Fore.CYAN}重试第{i}次...')

    if courselist:
        for course in courselist:
            courseId = course['courseId']
            courseId_desc = course['desc']
            _addcourseurl = 'https://2-class.com/api/course/addCoursePlayPV'
            for i in range(1, __try_time +1):
                try:
                    response = req_session.post(url=_addcourseurl,
                                                headers=headers_json,
                                                data=json.dumps({'courseId': courseId, 'reqtoken': reqtoken}),
                                                timeout=__time_out)
                    break
                except Exception as e:
                    print(Fore.RED + ' 播放视频失败,错误为：' + str(e))
                    if i <= __try_time:
                        print(f'{Fore.CYAN}重试第{i}次...')
               
            _TestPaperList_url = f'https://2-class.com/api/exam/getTestPaperList?courseId={courseId}'
            for i in range(__try_time):
                try:
                    testPaperList = req_session.get(_TestPaperList_url,verify=False).json()['data'].get('testPaperList')
                    break
                except Exception as e:
                    print(Fore.RED + ' 播放视频失败,错误为：' + str(e))
                    if i <= __try_time-1:
                        print(f'{Fore.CYAN}重试第{i+1}次...')                    
            if testPaperList:
                examCommitReqDataList = []
                for examId, paper in enumerate(testPaperList, 1):
                    examCommitReqDataList.append({'examId':examId, 'answer':paper['answer']})
            
                examcommit = {
                    "courseId":courseId,
                    "examCommitReqDataList":examCommitReqDataList,
                    "exam":"course",
                    "reqtoken":reqtoken
                    }

                _url_examcommit = 'https://2-class.com/api/exam/commit'
                for i in range(1, __try_time +1):
                    try:
                        response = req_session.post(url=_url_examcommit,
                                                    headers=headers_json,
                                                    data=json.dumps(examcommit),
                                                    timeout=__time_out).json()
                        if response.get('data'):
                            print(f'完成课程:{courseId_desc}')   
                            break
                    except Exception as e:
                        print(Fore.RED + ' 播放视频失败,错误为：' + str(e))
                        if i <= __try_time:
                            print(f'{Fore.CYAN}重试第{i}次...')

if __name__ == '__main__':
    print(Fore.CYAN + "anti_drug 正在启动...    " + time_log())
    identify_path = '3.xls'
    read_user_data(identify_path)
    len_identify_account = len(user_Data_all)
    for user_order, user_info in enumerate(user_Data_all):

        req_session, reqtoken = user_login(user_info['account'], user_info['pass'])
        with open('order.log','a') as f:
            f.write(f"当前学生，序号{user_order+1}:{user_info['account']}") 
        if req_session:

            courseplay(req_session, reqtoken)
            quiz(req_session, reqtoken)

            print(f"{Fore.CYAN}{user_order + 1}/{len_identify_account}已完成...")
            time.sleep(0.1)


#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# 创建日期: 2018/5/29
## www.zjer.cn 之江汇教育自动登录工具

__author__ = 'kylinpoet'

import requests
import time
import json
import re
import random
import urllib.parse
import schedule

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'Referer': 'http://yun.zjer.cn/index.php',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}
__try_time = 3


def print_time_line(pref=''):
    print(pref + '#-------------' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '------------->')


def time_log() -> str:
    return "  ###  " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + "  ###"


t_urls_info: list = []
user_Data_all: list = []


def test_user_login(userid='', userpass='', try_time=__try_time):
    i = 1
    for i in range(1, try_time + 1):
        try:
            req_session = requests.Session()

            response = req_session.get('http://yun.zjer.cn/index.php?r=portal/user/logout',
                                       headers=headers, timeout=10)

            login_url = 'http://yun.zjer.cn/index.php?r=portal/user/doLoginPortal&ajax=1&callback=jQuery17209088366810393329_1510879853036&userId={}&userPsw={}'
            response = req_session.get(login_url.format(userid, urllib.parse.quote(userpass)),
                                       headers=headers, timeout=10)

            # login_user_info = {'session': '', 'userinfo': '', 'order': 0, 'order_amount': 0}
            user_info_dict = {'name': '', 'account': '', 'password': '', 'sid': ''}

            response_json = json.loads(response.text[response.text.find('(') + 1:-1])

            resp_code = response_json.get('code')
            if resp_code == '000000':

                user_name = response_json['userinfo']['name']

                user_info_dict['name'] = response_json['userinfo']['name']
                user_info_dict['account'] = userid
                user_info_dict['password'] = userpass
                user_info_dict['sid'] = response_json['userinfo']['personid']
                print(f"{user_name:{chr(12288)}<5}测试登陆成功.{time_log()}")
                return user_info_dict

            else:
                print_time_line()
                print(userid, response_json.get('message'))
                if '密码错误' not in response_json.get('message'):
                    raise MyException('网站自报登录异常')
                else:
                    return {}
        except Exception as e:
            print_time_line()
            print(userid, '用户登录失败，错误提示为:', e)
            if i <= try_time:
                print(f'重试第{i}次')
            else:
                return {}


def read_user_data(filename='teacher_info.txt') -> list:
    """
    :param filename:
    :return: a list of user info dict
    """
    global user_Data_all
    user_Data_all = []
    user_info_dict = {'name': '', 'account': '', 'password': '', 'sid': ''}
    with open(filename, 'r', encoding='utf-8-sig') as file_object:
        global t_urls_info
        t_urls_info = []
        try:
            lines = file_object.readlines()
            for line in lines:
                try:
                    if (not line.startswith('#')) and (not line.replace(' ', '') == '\n'):
                        line_data = line.rstrip('\n').split('\t')
                        user_info_dict = test_user_login(line_data[0], line_data[1])  ###这里进行每个账号的测试
                        if len(user_info_dict) > 0:
                            # ('/index.php?r=space/person/index&sid=158486', '陈建林')
                            t_urls_info.append(('/index.php?r=space/person/index&sid=' + user_info_dict['sid'],
                                                user_info_dict['name']))
                            user_Data_all.append(user_info_dict.copy())
                            user_info_dict = {'name': '', 'account': '', 'password': '', 'sid': ''}
                except Exception as e:
                    print('验证账号失败:', e)
        except Exception as e:
            print(line, '读取账号信息失败，错误提示为：', e)
    return user_Data_all


class MyException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):  # 这里就是异常的字符串信息
        return self.message


def user_login(userid='', userpass='', user_order=0, user_amount=0, try_time=__try_time):
    i = 1
    for i in range(1, try_time + 1):
        try:
            req_session = requests.Session()
            # 这句好像没什么鸟用，还经常报错
            # response = req_session.get('http://yun.zjer.cn/index.php?r=portal/user/logout',
            #                           headers=headers, timeout=20)

            login_url = 'http://yun.zjer.cn/index.php?r=portal/user/doLoginPortal&ajax=1&callback=jQuery17209088366810393329_1510879853036&userId={}&userPsw={}'
            response = req_session.get(login_url.format(userid, urllib.parse.quote(userpass)),
                                       headers=headers, timeout=10)

            login_user_info = {'session': '', 'userinfo': '', 'order': 0, 'order_amount': 0}

            response_json = json.loads(response.text[response.text.find('(') + 1:-1])

            resp_code = response_json.get('code')
            if resp_code == '000000':

                user_name = response_json['userinfo']['name']
                # print(user_name + "login ok!", time_log())
                print(f"{user_name:{chr(12288)}<5}登陆成功.  {time_log()}")
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
            print(f'{userid}登录失败，错误提示为:', e)
            if i <= try_time:
                print(f'重试第{i}次...')
            else:
                return {}


def get_school_teacher(
        School_Teacher_url='http://yun.zjer.cn/index.php?r=space/school/portal/index/GetModuleHtml&name=Teacherlist&spacetype=schooltp&sid=shixun_xx14631'):
    # school_url = 'http://yun.zjer.cn/index.php?r=space/school/portal/index&sid=shixun_xx14631'
    try:
        response = requests.get(School_Teacher_url, headers=headers, timeout=10)

        regex = re.compile('<a href=\"(.+)\" title=\"(.+)\" target=')
        t_urls_info_x = regex.findall(response.text)
        return t_urls_info_x  # [('/index.php?r=space/person/index&sid=134426', '朱蕾'), ('/index.php?r=space/person/index&sid=136973', '林珍建')]
    except Exception as e:
        print('获取基地校教师信息失败，错误提示为：', e)
        print_time_line()


def visit_jdx(login_user_info,
              jdx_url=('http://jdx.zjer.cn/index.php?r=studio/pageview/clickview&sid=600046&url='
                       'cj1zdHVkaW8vaW5kZXgvaW5kZXgmc2lkPTYwMDA0Ng%3D%3D'),
              try_time=__try_time):
    # http://jdx.zjer.cn/index.php?r=studio/index&sid=600046
    i = 1
    for i in range(1, try_time + 1):
        try:
            response = login_user_info['session'].get(jdx_url, headers=headers, timeout=10)
            print(login_user_info['userinfo']['name'], '成功访问基地校! ')
            print_time_line()
            return 1
        except Exception as e:
            print(time_log(), '\n访问基地校失败，错误提示为：', e)
            if i <= 3:
                print(f'重试第{i}次...')
            else:
                return 0


def visit_teacher(login_user_info, _t_urls_info=[]):
    try:

        # visit_jdx(login_user_info)
        # 2019年5月9日 19:14:31 硬编码
        # _t_urls_info = [('/index.php?r=space/person/index&sid=158486', '陈建林'),
        #                 ('/index.php?r=space/person/index&sid=351313', '姜如意'),
        #                 ('/index.php?r=space/person/index&sid=583843', '林安典'),
        #                 ('/index.php?r=space/person/index&sid=134426', '朱蕾'),
        #                 ('/index.php?r=space/person/show&sid=216333', '林盈盈'),
        #                 ('/index.php?r=space/person/show&sid=15897', '季芙菲'),
        #                 ('/index.php?r=space/person/show&sid=52983', '潘春波')
        #                 ]

        _t_urls_info = t_urls_info.copy()

        # 2019年10月24日 11:04:29 手动添加
        _t_urls_info.extend([('/index.php?r=space/person/index&sid=272487', '舒义平'),
                             ('/index.php?r=space/person/index&sid=251381', '包晓红'),
                             ('/index.php?r=space/person/index&sid=278466', '郑妙君'),
                             ('/index.php?r=space/person/index&sid=170200', '赵晓阳'),
                             ('/index.php?r=space/person/show&sid=135904', '刘康康'),
                             ('/index.php?r=space/person/show&sid=199927', '单双红'),
                             ('/index.php?r=space/person/show&sid=717149', '毛丽军'),
                             ('/index.php?r=space/person/show&sid=353833', '杜丽君'),
                             ('/index.php?r=space/person/show&sid=334835', '冯惠云'),
                             ('/index.php?r=space/person/show&sid=249937', '黄小燕'),
                             ('/index.php?r=space/person/show&sid=138371', '李蕊'),
                             ('/index.php?r=space/person/show&sid=148433', '黄灵颖'),
                             ('/index.php?r=space/person/show&sid=54395', '张成丰'),
                             ('/index.php?r=space/person/show&sid=135905', '陈琼瑜'),
                             ('/index.php?r=space/person/show&sid=18573', '陈芳'),
                             ]
                            )
        mount_t_urls_info = len(_t_urls_info)
        for i, value in enumerate(_t_urls_info):  ### 超时错误处理（出错继续）还没做 2019年10月24日 14:24:57
            # ('/index.php?r=space/person/index&sid=134426', '朱蕾')
            url_get = value[0]
            url_get = url_get.replace('person/index', 'person/show')
            headers['Referer'] = 'http://yun.zjer.cn' + url_get

            response = login_user_info['session'].get(
                url='http://yun.zjer.cn/index.php?r=widgets/heartbeat/Heartbeat/Index&callback=GetHeartbeat&url=file:///C:/Users/kylin/Desktop/1.html&_=' '%d' % (
                        (time.time() + 3) * 1000), timeout=10)
            response = login_user_info['session'].get(
                url='http://yun.zjer.cn/?r=crontab/logs/page&starttime=' + '%.4f' % time.time() + '&url=' + url_get + '&_=' + '%d' % (
                        (time.time() + 3) * 1000), timeout=10)
            url_get = 'http://yun.zjer.cn' + value[0]
            url_get = url_get.replace('space/person', 'space/person/visitor')
            response = login_user_info['session'].get(url_get, headers=headers, data=json.dumps({'': ''}), timeout=10)
            response = login_user_info['session'].post(url='http://yun.zjer.cn/index.php?r=api/user/setUservv',
                                                       headers=headers,
                                                       data={"sid": login_user_info['userinfo']['personid']},
                                                       timeout=10)

            if '000000' in response.text or response.status_code == 500:
                print('{0}/{1}{2}成功踩了第{3}/{4}位教师{5}的空间。'.format(login_user_info['order'],
                                                                login_user_info['order_amount'],
                                                                login_user_info['userinfo']['name'],
                                                                i + 1, mount_t_urls_info, value[1]))
                # print_time_line()
            time.sleep(0.1)
    except Exception as e:
        print('访问教师失败,错误提示为：', e)
        print_time_line()


def visit_res(login_user_info):
    try:
        print('{}/{}{}开始进行资源处理...'.format(login_user_info['order'],
                                          login_user_info['order_amount'],
                                          login_user_info['userinfo']['name']))
        print_time_line()
        response = requests.get('http://res.zjer.cn/cms-portal/resListPage_Square.html', timeout=10)
        regex = re.compile('<span class=\"mglr15 txt\">共 (.+) 页')
        pagenums = int(regex.findall(response.text)[0])
        rand_pagenum = random.randint(1, pagenums)
        response = requests.get('http://res.zjer.cn/cms-portal/resListPage_Square.html?curPage={}'.format(rand_pagenum),
                                timeout=10)
        regex = re.compile('addCollectLabelMange\((.+)\);\" class=\"sc_a\">')
        reslist = regex.findall(response.text)  # 保存了十个信息，取三条
        for _ in range(1, 4):
            # ["'3befdebb6e1e4ba5a939b1df85116ffe'", "'第11课 公交站台设计.ppt'", "'第11课 公交站台设计.ppt'", "'14749696'", "'PD0013132516'", "''"]
            res_value = reslist[_].split(',')

            productCode = res_value[4].replace("'", '')
            fileLength = res_value[3].replace("'", '')
            resId = res_value[0].replace("'", '')
            title = res_value[1].replace("'", '')

            payload = 'study=1&flag=1&returnUrl=%2FgoResDetailInfo_Square.html%3FproductCode%3D{}'.format(productCode)
            response = login_user_info['session'].post('http://res.zjer.cn/cms-portal/judgeLogin.html',
                                                       data=payload, headers=headers, timeout=10)
            payload = 'productCode={}&score=4&scoreType=1'.format(productCode)  # 评分4分
            response = login_user_info['session'].post('http://res.zjer.cn/cms-portal/commentScore.html',
                                                       data=payload, headers=headers, timeout=10)
            if '"success": true' in response.text:
                print('资源{}评分成功'.format(_), end=',')
            else:
                print('资源{}评分失败'.format(_), end=',')

            # 2018年5月31日21:56:23 评论功能貌似关闭了,暂停
            # payload = 'productCode={}&commentContent={}&commentType=1&hasWord=0&content=http%3A%2F%2Fres.zjer.cn%2Fcms-portal%2FgoResDetailInfoDo_Square.do%3FproductCode%3D{}'
            # payload = payload.format(productCode, urllib.parse.quote('多谢分享 by chenjianlin'), productCode)
            # response = login_user_info['session'].post('http://res.zjer.cn/cms-portal/addComment.html',
            #                                            data=payload, headers=headers)
            # # "success": true
            # if '"success": true' in response.text:
            #     print('资源{}评论成功'.format(_), end=',')
            # else:
            #     print('资源{}评论失败'.format(_), end=',')

            payload = 'collectionType=1&productCode={}&productName=&fileName=&fileLength={}&labelManage=%E5%AD%A6%E4%B9%A0%E8%B5%84%E6%96%99&resId={}&title={}'
            payload = payload.format(productCode, fileLength, resId, urllib.parse.quote(title))
            response = login_user_info['session'].post('http://res.zjer.cn/cms-portal/prodCollect.html',
                                                       data=payload, headers=headers, timeout=10)
            if '"result": "000000"' in response.text:
                print('资源{}收藏成功'.format(_), end='\n')
            else:
                print('资源{}收藏失败'.format(_), end='\n')
            print('{}/{}{}资源处理结束.'.format(login_user_info['order'],
                                          login_user_info['order_amount'],
                                          login_user_info['userinfo']['name']))

    except Exception as e:
        print('访问资源错误,错误提示为：', e)
        print_time_line()


def visit_ms(login_user_info):
    topic_content = '这个话题好！学习了。每一次的阅读都是一次学习，每一次的学习都收获满满！'  # 三十个字
    try:
        print('{}/{}{}开始访问名师工作室...'.format(
            login_user_info['order'],
            login_user_info['order_amount'],
            login_user_info['userinfo']['name']))
        print_time_line()

        ms_url = 'http://ms.zjer.cn/index.php?r=studio/master/ajaxstudio&c=&grade=&sitecode=&type=now&order=desc&orderby=&prd=&sub=&area=&city=&studioname=&page='
        response = requests.get(ms_url, timeout=10)
        regex = re.compile('page=(\d+)\">尾页</a>')
        pagenums = int(regex.findall(response.text)[0])
        rand_pagenum = random.randint(1, pagenums)
        response = requests.get(ms_url + str(rand_pagenum), timeout=10)

        regex = re.compile('<a href=\"(.+)\" target=')
        ms_list = regex.findall(response.text)
        ms_url_1 = random.choice(ms_list)

        ms_url_2 = ms_url_1 + '/?r=studio/topic/index'
        response = login_user_info['session'].get(ms_url_2, timeout=10)
        regex = re.compile('<a href=\"/index.php\?r=studio/topic/show&(.+)\">')
        _ = random.choice((regex.findall(response.text))).replace('&id', '&tid')
        ms_topic1_url = ms_url_1 + '/index.php?r=studio/topic/replyajax&' + _
        payload = 'content={}&ajax_page=1&isjoin=0'.format(urllib.parse.quote(topic_content))
        response = login_user_info['session'].post(ms_topic1_url, data=payload, headers=headers, timeout=10)
        if '{"status":""}' in response.text:
            print('名师工作室评论成功')
        else:
            print('名师工作室评论失败')

        print('{}/{}{}访问名师工作室结束.'.format(
            login_user_info['order'],
            login_user_info['order_amount'],
            login_user_info['userinfo']['name'])
        )
    except Exception as e:
        print('访问名师工作室错误：错误提示为：', e)
        print_time_line()


def visit_msgzs(login_user_info,
                ms_url='http://panchunbo.ms.zjer.cn/index.php?r=studio/pageview&sid=292&pgurl=%2F',
                try_time=__try_time):
    """名师工作室每小时访问增加访问量"""
    # http://panchunbo.ms.zjer.cn
    i = 1
    for i in range(1, try_time + 1):
        try:
            response = login_user_info['session'].get(ms_url, headers=headers, timeout=10)
            print(f"{login_user_info['userinfo']['name']:{chr(12288)}<5}成功访问名师工作室!")
            return 1
        except Exception as e:
            print(time_log(), '访问名师工作室失败，错误提示为：', e)
            if i <= try_time:
                print(f'重试第{i}次...')
            else:
                return 0


# __global_topic_url = ['http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1957547',
#                       'http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1957529',
#                       'http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1986965',
#                       'http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1984023',
#                       'http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1972219',
#                       'http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1983907',
#                       'http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1976445']

__global_topic_url = ['http://ms.zjer.cn/index.php?r=studio/post/view&sid=292&id=1984709']

def visit_msgzs_topic(login_user_info, topic_url=[], try_time=__try_time):
    try:
        for topic_url1 in topic_url:
            regex = re.compile('sid=(\d+)&id=(\d+)')
            topic_temp = re.split(regex, topic_url1)
            sid, topic_id = topic_temp[1], topic_temp[2]
            # 访问名师文章记录

            topic_real_url = 'http://ms.zjer.cn/index.php?r=studio/pageview&sid=' + sid + \
                             '&pgurl=/index.php?r=studio/post/view&sid=' + sid + '&id=' + topic_id
            i = 1
            for i in range(1, try_time + 1):
                try:
                    response = login_user_info['session'].get(topic_url1, headers=headers, timeout=10)
                    time.sleep(0.1)
                    response = login_user_info['session'].get(topic_real_url, headers=headers, timeout=10)
                    print(f"{login_user_info['userinfo']['name']:{chr(12288)}<5}访问文章{topic_id}成功")
                    break
                except Exception as e:
                    print(time_log(), '访问名师工作室文章失败，错误提示为：', e)
                    if i <= try_time:
                        print(f'重试第{i}次...')
                    else:
                        print('访问文章失败')

            # 评分
            star_url = 'http://ms.zjer.cn/index.php?r=studio/resources/newstar&sid=' + sid
            response = login_user_info['session'].post(url=star_url,
                                                       headers=headers,
                                                       data={"score": '5', "type": '3', 'id': topic_id, 'resid': topic_id},
                                                       timeout=10)
            print(f"{login_user_info['userinfo']['name']:{chr(12288)}<5}{response.json().get('content','')}")
            # 赞
            like_url = 'http://ms.zjer.cn/index.php?r=studio/post/like&sid=' + sid
            i = 1
            for i in range(1, try_time + 1):
                try:
                    response = login_user_info['session'].post(url=like_url,
                                                               headers=headers,
                                                               data={'id': topic_id, 'ajax': '1'},
                                                               timeout=10)
                    print(f"{login_user_info['userinfo']['name']:{chr(12288)}<5}{response.json().get('message', '')}")
                    break
                except Exception as e:
                    print(time_log(), '点赞文章失败，错误提示为：', e)
                    if i <= try_time:
                        print(f'重试第{i}次...')
                    else:
                        print('点赞文章失败')

            # 获取收藏目录
            postview_url = 'http://ms.zjer.cn/index.php?r=studio/post/postview&sid=' + sid
            space_cat_id = ''
            i = 1
            for i in range(1, try_time + 1):
                try:
                    response = login_user_info['session'].get(postview_url, headers=headers, timeout=10)
                    regex = re.compile('<option value="(\d+)">')
                    space_cat_id_regex = re.findall(regex, response.text)
                    if space_cat_id_regex:
                        space_cat_id = space_cat_id_regex[0]
                    else:
                        space_cat_id = 'null'
                    # print(f"{login_user_info['userinfo']['name']:{chr(12288)}<5}{response.json().get('content', '')}")
                    break
                except Exception as e:
                    print(time_log(), '获取收藏目录，错误提示为：', e)
                    if i <= try_time:
                        print(f'重试第{i}次...')
                    else:
                        print('获取收藏目录失败')

            # 收藏文章
            postspace_url = f'http://ms.zjer.cn/index.php?r=studio/post/postspace&sid={sid}&id={topic_id}&space_cat_id={space_cat_id}'
            i = 1
            for i in range(1, try_time + 1):
                try:
                    response = login_user_info['session'].get(postspace_url, headers=headers, timeout=10)
                    print(f"{login_user_info['userinfo']['name']:{chr(12288)}<5}{response.json().get('message', '')}")
                    break
                except Exception as e:
                    print(time_log(), '收藏文章失败，错误提示为：', e)
                    if i <= try_time:
                        print(f'重试第{i}次...')
                    else:
                        print('收藏文章失败')
    except:
        print('访问名师工作室文章错误')


def zjer_call_action(identify_path='teacher_info.txt', action=[]):
    # global t_urls_info
    # identify_account = read_user_data(identify_path)
    # 
    read_user_data(identify_path)
    len_identify_account = len(user_Data_all)

    for user_order, user_info in enumerate(user_Data_all):

        user_login_info = user_login(user_info['account'],
                                     user_info['password'],
                                     user_order + 1,
                                     len_identify_account)
        time.sleep(1)
        if user_login_info:
            for act in action:
                if act == 'login_jdx':
                    # visit_teacher(user_login_info, t_urls_info)
                    visit_jdx(user_login_info)
                elif act == 'visit_ms':
                    # visit_res(user_login_info)
                    visit_ms(user_login_info)

                elif act == 'visit_teacher':
                    visit_teacher(user_login_info)
                elif act == 'visit_msgzs':
                    visit_msgzs(user_login_info)
                elif act == 'visit_msgzs_topic':
                    visit_msgzs_topic(user_login_info, topic_url=__global_topic_url)
                time.sleep(1)


# 2019年5月9日 12:37:33 暂时屏蔽
# t_urls_info = get_school_teacher()


if __name__ == '__main__':

    print("zj_zuto 正在启动... ", time_log())
    identify_path = '1.txt'
    zjer_call_action(identify_path=identify_path, action=['visit_msgzs_topic'])
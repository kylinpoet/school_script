#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 创建日期: 2018/5/29
# www.zjer.cn 之江汇教育自动登录工具

__author__ = 'kylinpoet'

import requests
import time
import json
import re
import random
import urllib.parse
import schedule
from colorama import Fore, init
from tenacity import *
__hitokoto_api = 'https://v1.hitokoto.cn/?encode=text'
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


def test_user_login(userid='', userpass='', try_time=__try_time):
    i = 1
    for i in range(1, try_time + 1):
        try:
            req_session = requests.Session()

            response = req_session.get(
                'http://yun.zjer.cn/index.php?r=portal/user/logout',
                headers=headers,
                timeout=__time_out)

            login_url = 'http://yun.zjer.cn/index.php?r=portal/user/doLoginPortal&ajax=1&callback=jQuery17209088366810393329_1510879853036&userId={}&userPsw={}'
            response = req_session.get(
                login_url.format(
                    userid,
                    urllib.parse.quote(userpass)),
                headers=headers,
                timeout=__time_out)

            # login_user_info = {'session': '', 'userinfo': '', 'order': 0, 'order_amount': 0}
            user_info_dict = {
                'name': '',
                'account': '',
                'password': '',
                'sid': '',
                'session': ''}

            response_json = json.loads(
                response.text[response.text.find('(') + 1:-1])

            resp_code = response_json.get('code')
            if resp_code == '000000':
                user_name = response_json['userinfo']['name']
                user_info_dict['name'] = response_json['userinfo']['name']
                user_info_dict['account'] = userid
                user_info_dict['password'] = userpass
                user_info_dict['sid'] = response_json['userinfo']['personid']
                user_info_dict['session'] = req_session
                print(f"{Fore.GREEN}{user_name:{chr(12288)}<5}测试登陆成功.{time_log()}")
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
            print(Fore.RED + userid + '用户登录失败，错误提示为:' + str(e))
            if i <= try_time:
                print(f'{Fore.BLUE}重试第{i}次')
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
                    if (not line.startswith('#')) and (
                            not line.replace(' ', '') == '\n'):
                        line_data = line.rstrip('\n').split('\t')
                        user_info_dict = test_user_login(
                            line_data[0], line_data[1])  # 这里进行每个账号的测试
                        if len(user_info_dict) > 0:
                            # ('/index.php?r=space/person/index&sid=158486', '陈建林')
                            t_urls_info.append(
                                ('/index.php?r=space/person/index&sid=' +
                                 user_info_dict['sid'],
                                    user_info_dict['name']))
                            user_Data_all.append(user_info_dict.copy())
                            user_info_dict = {
                                'name': '',
                                'account': '',
                                'password': '',
                                'sid': '',
                                'session': ''}
                except Exception as e:
                    print('验证账号失败:', str(e))
        except Exception as e:
            print(Fore.RED + line + '读取账号信息失败，错误提示为：' + str(e))
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
            # 这句好像没什么鸟用，还经常报错
            # response = req_session.get('http://yun.zjer.cn/index.php?r=portal/user/logout',
            #                           headers=headers, timeout=20)

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


def get_school_teacher(
        School_Teacher_url='http://yun.zjer.cn/index.php?r=space/school/portal/index/GetModuleHtml&name=Teacherlist&spacetype=schooltp&sid=shixun_xx14631'):
    # school_url = 'http://yun.zjer.cn/index.php?r=space/school/portal/index&sid=shixun_xx14631'
    try:
        response = requests.get(
            School_Teacher_url,
            headers=headers,
            timeout=__time_out)

        regex = re.compile('<a href=\"(.+)\" title=\"(.+)\" target=')
        t_urls_info_x = regex.findall(response.text)
        # [('/index.php?r=space/person/index&sid=134426', '朱蕾'), ('/index.php?r=space/person/index&sid=136973', '林珍建')]
        return t_urls_info_x
    except Exception as e:
        print('获取基地校教师信息失败，错误提示为：', e)
        print_time_line()


def visit_jdx(
        login_user_info,
        jdx_url=(
            'http://jdx.zjer.cn/index.php?r=studio/pageview/clickview&sid=600046&url='
            'cj1zdHVkaW8vaW5kZXgvaW5kZXgmc2lkPTYwMDA0Ng%3D%3D'),
        try_time=__try_time):
    # http://jdx.zjer.cn/index.php?r=studio/index&sid=600046
    i = 1
    for i in range(1, try_time + 1):
        try:
            response = login_user_info['session'].get(
                jdx_url, headers=headers, timeout=__time_out)
            print(Fore.GREEN + login_user_info['userinfo']['name'] + '成功访问基地校! ')
            print_time_line()
            return 1
        except Exception as e:
            print(time_log(), '\n访问基地校失败，错误提示为：', e)
            if i <= 3:
                print(f'重试第{i}次...')
            else:
                return 0

@retry(
    retry=retry_if_exception_type(),
    stop=stop_after_attempt(3),
    after=try_log)
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
        for i, value in enumerate(
                _t_urls_info):
            # ('/index.php?r=space/person/index&sid=134426', '朱蕾')
            url_get = value[0]
            url_get = url_get.replace('person/index', 'person/show')
            headers['Referer'] = 'http://yun.zjer.cn' + url_get

            response = login_user_info['session'].get(
                url='http://yun.zjer.cn/index.php?r=widgets/heartbeat/Heartbeat/Index&callback=GetHeartbeat&url=file:///C:/Users/kylin/Desktop/1.html&_='
                '%d' %
                ((time.time() + 3) * 1000), timeout=__time_out)
            response = login_user_info['session'].get(
                url='http://yun.zjer.cn/?r=crontab/logs/page&starttime=' + '%.4f' %
                time.time() + '&url=' + url_get + '&_=' + '%d' %
                ((time.time() + 3) * 1000), timeout=__time_out)
            url_get = 'http://yun.zjer.cn' + value[0]
            url_get = url_get.replace('space/person', 'space/person/visitor')
            response = login_user_info['session'].get(
                url_get, headers=headers, data=json.dumps({'': ''}), timeout=__time_out)
            response = login_user_info['session'].post(
                url='http://yun.zjer.cn/index.php?r=api/user/setUservv',
                headers=headers,
                data={
                    "sid": login_user_info['userinfo']['personid']},
                timeout=__time_out)

            if '000000' in response.text or response.status_code == 500:
                print(Fore.GREEN +
                      '{0}/{1}{2}成功踩了第{3}/{4}位教师{5}的空间。'.format(
                          login_user_info['order'],
                          login_user_info['order_amount'],
                          login_user_info['userinfo']['name'],
                          i + 1,
                          mount_t_urls_info,
                          value[1]))
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
        response = requests.get(
            'http://res.zjer.cn/cms-portal/resListPage_Square.html',
            timeout=__time_out)
        regex = re.compile('<span class=\"mglr15 txt\">共 (.+) 页')
        pagenums = int(regex.findall(response.text)[0])
        rand_pagenum = random.randint(1, pagenums)
        response = requests.get(
            'http://res.zjer.cn/cms-portal/resListPage_Square.html?curPage={}'.format(rand_pagenum),
            timeout=__time_out)
        regex = re.compile(r'addCollectLabelMange\((.+)\);\" class=\"sc_a\">')
        reslist = regex.findall(response.text)  # 保存了十个信息，取三条
        for _ in range(1, 4):
            # ["'3befdebb6e1e4ba5a939b1df85116ffe'", "'第11课 公交站台设计.ppt'", "'第11课 公交站台设计.ppt'", "'14749696'", "'PD0013132516'", "''"]
            res_value = reslist[_].split(',')

            productCode = res_value[4].replace("'", '')
            fileLength = res_value[3].replace("'", '')
            resId = res_value[0].replace("'", '')
            title = res_value[1].replace("'", '')

            payload = 'study=1&flag=1&returnUrl=%2FgoResDetailInfo_Square.html%3FproductCode%3D{}'.format(
                productCode)
            response = login_user_info['session'].post(
                'http://res.zjer.cn/cms-portal/judgeLogin.html',
                data=payload,
                headers=headers,
                timeout=__time_out)
            payload = 'productCode={}&score=4&scoreType=1'.format(
                productCode)  # 评分4分
            response = login_user_info['session'].post(
                'http://res.zjer.cn/cms-portal/commentScore.html',
                data=payload,
                headers=headers,
                timeout=__time_out)
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
            payload = payload.format(
                productCode,
                fileLength,
                resId,
                urllib.parse.quote(title))
            response = login_user_info['session'].post(
                'http://res.zjer.cn/cms-portal/prodCollect.html',
                data=payload,
                headers=headers,
                timeout=__time_out)
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
        response = requests.get(ms_url, timeout=__time_out)
        regex = re.compile(r'page=(\d+)\">尾页</a>')
        pagenums = int(regex.findall(response.text)[0])
        rand_pagenum = random.randint(1, pagenums)
        response = requests.get(ms_url + str(rand_pagenum), timeout=__time_out)

        regex = re.compile('<a href=\"(.+)\" target=')
        ms_list = regex.findall(response.text)
        ms_url_1 = random.choice(ms_list)

        ms_url_2 = ms_url_1 + '/?r=studio/topic/index'
        response = login_user_info['session'].get(ms_url_2, timeout=__time_out)
        regex = re.compile(
            r'<a href=\"/index.php\?r=studio/topic/show&(.+)\">')
        _ = random.choice(
            (regex.findall(
                response.text))).replace(
            '&id', '&tid')
        ms_topic1_url = ms_url_1 + '/index.php?r=studio/topic/replyajax&' + _
        payload = 'content={}&ajax_page=1&isjoin=0'.format(
            urllib.parse.quote(topic_content))
        response = login_user_info['session'].post(
            ms_topic1_url, data=payload, headers=headers, timeout=__time_out)
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


def visit_msgzs(
        login_user_info,
        ms_url='http://panchunbo.ms.zjer.cn/index.php?r=studio/pageview&sid=292&pgurl=%2F',
        try_time=__try_time):
    """名师工作室每小时访问增加访问量"""
    # http://panchunbo.ms.zjer.cn
    i = 1
    for i in range(1, try_time + 1):
        try:
            response = login_user_info['session'].get(
                ms_url, headers=headers, timeout=__time_out)
            print(
                f"{Fore.GREEN}{login_user_info['userinfo']['name']:{chr(12288)}<5}成功访问名师工作室!")
            return 1
        except Exception as e:
            print(Fore.RED + time_log() + '访问名师工作室失败，错误提示为：' + str(e))
            if i <= try_time:
                print(f'{Fore.CYAN}重试第{i}次...')
            else:
                return 0



@retry(
    retry=retry_if_exception_type(),
    stop=stop_after_attempt(3),
    after=try_log)
def rand_text():
    response = requests.get(__hitokoto_api)
    return response.text


url_BlogAdd_Draft = 'http://yun.zjer.cn/index.php?r=widgets/mm_center_person/blog/blogadd/BlogAdd/Draft'


@retry(
    retry=retry_if_exception_type(),
    stop=stop_after_attempt(3),
    after=try_log)
def get_categoryid(login_user_info):
    regex = re.compile(r'value="(\d+)">.*</option>')
    # 'http://yun.zjer.cn/index.php?r=widget&classname=widgets.mm_center_person.blog.blogadd.BlogAddWidget&kid=c8a3462f1f9786c078f8b5a8ddc03271&_=1573010101682'
    url = 'http://yun.zjer.cn/index.php?r=widget&classname=widgets.mm_center_person.blog.blogadd.BlogAddWidget'
    response = login_user_info['session'].get(
        url, headers=headers, timeout=__time_out)
    space_cat_id_regex = re.findall(regex, response.text)
    if space_cat_id_regex:
        categoryid = space_cat_id_regex[0]
    else:
        categoryid = 'null'
    return categoryid

@retry(
    retry=retry_if_exception_type(),
    stop=stop_after_attempt(3),
    after=try_log)
def Blog_Add(login_user_info, title=urllib.parse.quote('今日成果'),
             content=urllib.parse.quote(f'<p>{rand_text()}</p>')):
    # 这三条提交不知道是干嘛的，也许是为了给访问者加分？暂时保留
    # response = login_user_info['session'].post(url='http://yun.zjer.cn/index.php?r=api/user/setUservv',
    #                                            headers=headers,
    #                                            data={"sid": login_user_info['userinfo']['personid']},
    #                                            timeout=__time_out)
    # response = login_user_info['session'].get(
    #     url='http://yun.zjer.cn/?r=crontab/logs/page&starttime=' + '%.4f' % time.time() + '&url=' + '%2Findex.php%3Fr%3Dcenter%2Fperson%2Fblog%2Fadd' + '&_=' + '%d' % (
    #             (time.time() + 3) * 1000), timeout=__time_out)

    try:
        categoryid = get_categoryid(login_user_info)
        url_BlogAdd_Draft = 'http://yun.zjer.cn/index.php?r=widgets/mm_center_person/blog/blogadd/BlogAdd/Draft'
        payload = f'id=&draftid=&status=&title={title}&content={content}&categoryid=\
    {categoryid}&external_type=public&tags=&istop=untop&comment_status=open&copy_status=open&credit=0\
    &experience=0&password=&publisher=&original_type=1&original_type_url=&resource='
        response = login_user_info['session'].post(
            url_BlogAdd_Draft, data=payload, headers=headers, timeout=__time_out)
        # 获取，保存临时id
        draftid = response.json().get('draftid', '')

        # 发文
        url_BlogAdd_Publish = 'http://yun.zjer.cn/index.php?r=widgets/mm_center_person/blog/blogadd/BlogAdd/Publish'
        payload = f'id=0&draftid={draftid}&publishid=0&status=&title={title}&content={content}&categoryid=\
    {categoryid}&external_type=public&tags=&istop=untop&comment_status=open&copy_status=open&credit=0&experience=0\
    &password=&publisher=&original_type=1&original_type_url=&resource=&coverpublish=0&class_contribute=&w='
        response = login_user_info['session'].post(
            url_BlogAdd_Publish, data=payload, headers=headers, timeout=__time_out)
        print(
            f"{login_user_info['userinfo']['name']}{response.json().get('message', '')}{response.json().get('id',None)}")
        return response.json().get('id', None)
    except Exception as e:
        print(f'{Fore.RED}发表文章失败.{e}')
        return


# 2019年5月9日 12:37:33 暂时屏蔽
# t_urls_info = get_school_teacher()
#
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
        if user_login_info:
            user_Data_all[user_order]['session'] = user_login_info['session']
        time.sleep(1)
        if user_login_info:
            for act in action:
                if act == 'Blog_Add':
                    # 获取发表成果ID
                    blog_id = Blog_Add(user_login_info)
                    ## 确保发表成果成功
                    if blog_id:
                        user_list = list(range(len_identify_account))
                        user_list.remove(user_order)
                        i = 0
                        # 其他账号点赞，并且只用收藏两次
                        while len(user_list) >= 1:
                            other_user_order = random.choice(user_list)
                            user_list.remove(other_user_order)
                            i = i + 1

                            # 防止错误，尝试多次收藏
                            for j in range(1, __try_time + 1):
                                try:
                                    url = f'http://yun.zjer.cn/index.php?r=widgets/mm_center_person/blog/blogview/BlogView/FavoriteBlog&id={blog_id}&action=1&_=' + '%d' % ((time.time() + 3) * 1000)
                                    response = user_Data_all[other_user_order]['session'].get(url, headers=headers, timeout=__time_out)
                                    print(f"{Fore.GREEN}{blog_id}被{user_Data_all[other_user_order]['name']}{response.json().get('message', '')}")
                                    break
                                except Exception as e:
                                    print(f'{Fore.RED}{time_log()}\n收藏文章失败，错误提示为：{e}')
                                    if j <= 3:
                                        print(f'{Fore.CYAN}重试第{j}次...')
                                        sleep(1)
                                    else:
                                        break
                            if i == 2:
                                break
                        # 删除 blog_id
                        for i in range(1, __try_time + 1):
                            try:
                                url = f'http://yun.zjer.cn/index.php?r=widgets/mm_center_person/blog/bloglist/BlogList/DelBlog&id={blog_id}&_=' + '%d' % (
                                        (time.time() + 3) * 1000)
                                response = user_login_info['session'].get(
                                    url, headers=headers, timeout=__time_out)
                                print(f"{Fore.GREEN}{blog_id}{response.json().get('message', '')}")
                                break
                            except Exception as e:
                                print(f'{Fore.RED}{time_log()}\n删除文章失败，错误提示为：{e}')
                                if i <= 3:
                                    print(f'{Fore.CYAN}重试第{i}次...')
                                    sleep(1)
                                else:
                                    break
                else:
                    eval(f'{act}(user_login_info)')
                time.sleep(1)


"""
class visit_teacher(object,school_url=''):
    def get_teacher():
    def __init__(self)

        get_school_teacher
    ## log函数写文件

"""
if __name__ == '__main__':
    # zjer_call_action(action=['login_jdx', 'visit_ms_res'])
    # zjer_call_action(action=['visit_teacher'])
    # zjer_call_action(action=['visit_msgzs'])
    pass
    # # 以下2019.05.09执行
    # # # 资源评分和名师工作室评论一天一次，用户登录一个小时一次
    # # schedule.every(61).to(71).minutes.do(zjer_call_action, identify_path='student_info.txt', action='login_jdx')
    print(Fore.CYAN + "zj_zuto 正在启动...    " + time_log())
    identify_path = 'teacher_info.txt'
    zjer_call_action(action=['visit_msgzs'])
    zjer_call_action(action=['Blog_Add'])
    zjer_call_action(action=['visit_teacher'])
    zjer_call_action(action=['visit_jdx'])
    schedule.every(65).minutes.do(zjer_call_action, action=['visit_msgzs'])
    schedule.every(1).minute.do(print_time_line, pref='Heartbeat:')
    schedule.every().day.at("00:30").do(
        zjer_call_action, action=[
            'visit_jdx', 'visit_teacher', 'Blog_Add'])
    while True:
        schedule.run_pending()
        time.sleep(1)

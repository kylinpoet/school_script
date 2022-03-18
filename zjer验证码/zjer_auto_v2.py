from re import I
import re
import pytesseract
from PIL import Image, ImageEnhance
import requests
import os
import base64
from io import BytesIO
import urllib.parse
import time
from colorama import Fore, init
import schedule
init(autoreset=True)


tessconfig = r'--tessdata-dir "D:\\soft\\jTessBoxEditor\\tesseract-ocr\\tessdata"  \
    --psm 7 -c tessedit_char_whitelist=0123456789_=+?'

vcode_url = 'http://yun.zjer.cn/index.php?r=portal/Vcode/GetNewCode'

user_Data_all = []
def read_user_data(filename='teacher_info.txt') -> list:
    """
    :param filename:
    :return: a list of user info dict
    """
    global user_Data_all
    user_Data_all = []
    user_info_dict = {'account': '', 'password': '', 'name': '', 'sid': ''}
    with open(filename, 'r', encoding='utf-8-sig') as file_object:
        try:
            lines = file_object.readlines()
            for line in lines:
                try:
                    if (not line.startswith('#')) and (
                            not line.replace(' ', '') == '\n'):
                        line_data = line.rstrip('\n').split('\t')
                        user_info_dict['account'] = line_data[0]
                        user_info_dict['password'] = line_data[1]
                        user_info_dict['name'] = line_data[2]
                        user_Data_all.append(user_info_dict)
                        user_info_dict = {'account': '', 'password': '', 'name': '', 'sid': ''}
                except Exception as e:
                    print('验证账号失败:', str(e))
        except Exception as e:
            print(Fore.RED + line + '读取账号信息失败，错误提示为：' + str(e))
    return user_Data_all





class imageCode2str:
    """验证码转换为str"""

    def __init__(self, img_data) -> None:
        self.img_data = img_data

    def binaryzation(self, threshold=240):  # 降噪，图片二值化
        table = []
        for i in range(256):
            if i < threshold:
                table.append(1)
            else:
                table.append(0)
        return table

    def image_binaryzation(self):
        image = Image.open(BytesIO(self.decode_image())) # 打开图片
        image = image.convert('L')  # 转化为灰度图
        image = image.point(self.binaryzation(), '1')  # 二值化
        return image
    def image2str(self):
        ocr_result = pytesseract.image_to_string(
            self.image_binaryzation(), lang='zjer', config=tessconfig)
        result = ocr_result[:ocr_result.find('=')]
        return result

    def decode_image(self):
        """
        解码图片
        :param src: 图片编码
            eg:
                src="data:image/gif;base64,R0lGODlhMwAxAIAAAAAAAP///
                    yH5BAAAAAAALAAAAAAzADEAAAK8jI+pBr0PowytzotTtbm/DTqQ6C3hGX
                    ElcraA9jIr66ozVpM3nseUvYP1UEHF0FUUHkNJxhLZfEJNvol06tzwrgd
                    LbXsFZYmSMPnHLB+zNJFbq15+SOf50+6rG7lKOjwV1ibGdhHYRVYVJ9Wn
                    k2HWtLdIWMSH9lfyODZoZTb4xdnpxQSEF9oyOWIqp6gaI9pI1Qo7BijbF
                    ZkoaAtEeiiLeKn72xM7vMZofJy8zJys2UxsCT3kO229LH1tXAAAOw=="

        :return: str 保存到本地的文件名
        """
        # 1、信息提取
        result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", self.img_data, re.DOTALL)
        if result:
            ext = result.groupdict().get("ext")
            data = result.groupdict().get("data")
        else:
            raise Exception("Do not parse!")
        # 2、base64解码
        img = base64.b64decode(data)
        # 3、二进制文件保存
        return img


def _encrypt_string(str_value):

    key = 'tPhCyUsKpXlHsEgSyHoEkLdQpLkOsLcYhErFkWxJsFeVhLiQrHqFbYbNyEvClEwUfQmEgUnEfJiHfPtLuEdDbIiIqUqLoTzOmYqA'
    key_login = '95a1446a7120e4af5c0c8878abb7e6d2'
    str_base = base64.b64encode(bytes(str_value.encode('utf-8'))).decode('utf-8')
    key_len = len(key)
    code = ''
    newcode = ''

    for i in range(len(str_base)):
        k = i % key_len
        code += chr(ord(str_base[i]) ^ ord(key[k]))

    code = base64.b64encode(bytes(code.encode('utf-8'))).decode('utf-8')
    code_arr = list(code)
    key_arr = list(key)
    for j in range(len(code)):
        t1 = ''
        t2 = ''
        t1 = code_arr[j]
        if len(key_arr) > j:
            t2 = key_arr[j]
        newcode += t1+t2

    newcode = newcode.replace('/', "6666cd76f96956469e7be39d750cc7d9")
    newcode = newcode.replace('=', "43ec3e5dee6e706af7766fffea512721")
    newcode = newcode.replace('+', "26b17225b626fb9238849fd60eabdf60")
    newcode = key_login + newcode
    return newcode


class CustomException(Exception):
    pass

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'Referer': 'http://yun.zjer.cn/index.php',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
__try_time = 3
__time_out = 15

def print_time_line(pref='---'):
    print(f"{Fore.CYAN}### {pref} ### -------------{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}------------->")

def test_user_login(userid='', userpass='', try_time=__try_time):
    for i in range(1, try_time + 1):
        try:
            req_session = None
            req_session = requests.Session()
            # response = req_session.get(
            #     'http://yun.zjer.cn/index.php?r=portal/user/logout',
            #     headers=headers,
            #     timeout=__time_out)

            response = req_session.get(
            'http://yun.zjer.cn/space/index.php?r=portal/user/login',
            headers=headers,
            timeout=__time_out)
            time.sleep(2)
            for j in range(10):
                response = req_session.get(
                vcode_url,
                headers=headers,
                timeout=__time_out).json()
                imageinfo = response['imageinfo']
                passCode = response['passCode']
                str_valCode = imageCode2str(imageinfo).image2str()
                if str_valCode.endswith('\n'):
                    time.sleep(1)
                    print('验证码重试')
                    continue
                else:
                    valCode = eval(str_valCode)
                    break
            if j == 9:
                raise Exception('验证码识别错误')
            time.sleep(1)
            post_data = f'userId={_encrypt_string(userid)}&userPsw={_encrypt_string(userpass)}&vaildata={passCode}&valCode={valCode}'
            login_url = 'http://yun.zjer.cn/index.php?r=portal/user/loginNew'
            response_json = req_session.post(login_url, post_data, headers=headers, timeout=__time_out).json()
            resp_code = response_json.get('code')
            token = response_json.get('token')
            url_login_ticket = response_json.get('url')
            if resp_code == '000000':
                print(Fore.GREEN + userid + '登录成功')
            elif resp_code == '222222':
                raise Exception(response_json.get('message'))
            # oh.zjer.cn  wz.zjer.cn  sns.zjer.cn
            url = f'http://yun.zjer.cn/index.php?r=uc/loginToken&token={token}'
            response = req_session.get(url, headers=headers, timeout=__time_out)
            url = f'http://yun.zjer.cn/space/index.php?r=uc/loginToken&token={token}'
            response = req_session.get(url, headers=headers, timeout=__time_out)

            # response = req_session.get(url_login_ticket, headers=headers, timeout=__time_out)
            return req_session
            # 查看经验值
            url = 'http://yun.zjer.cn/space/index.php?r=center/person/ucenter/experience'
            'http://yun.zjer.cn/index.php?r=widgets/mm_center_person/40/ucenter/experience/Experience/Detail&starttime=2021-07-05&endtime=2021-07-13&type=1'        
            

        except Exception as e:
            print_time_line()
            print(Fore.RED + userid + '用户登录失败，错误提示为:' + str(e))
            if i <= try_time:
                print(f'{Fore.BLUE}重试第{i}次')
            else:
                return {}


def jdx_exp(req_s:requests.sessions.Session):
    # 访问过的不行。。。
    for i in range(1, __try_time + 1):
        # 先获取基地校最新课程
        try:
            url = 'http://jdx.zjer.cn/index.php?r=studio/square/StudioSquareCourseCenterIndex&isfromlistpage=1&pagesize=1'
            resp = req_s.get(url, headers=headers, timeout=__time_out)
            # 基地校经验获取地址
            result = re.search('<a href="(?P<class_url>.*)" class="zbkc_lsa"', resp.text, re.DOTALL)
            if result:
                class_url = result.groupdict().get("class_url")
            else:
                raise Exception("Do not parse!")

            url = 'http://jdx.zjer.cn' + class_url
            resp = req_s.get(url, headers=headers, timeout=__time_out)
            # 课程地址
            result = re.search("""\('#ajaxlist'\).load\("(?P<course_url>.*)", function""", resp.text, re.DOTALL)
            if result:
                course_url = result.groupdict().get("course_url")
            else:
                raise Exception("Do not parse!")

            url = 'http://jdx.zjer.cn' + course_url
            resp = req_s.get(url, headers=headers, timeout=__time_out)
            # 视频地址
            result = re.search('"观看视频" href="(?P<video_url>.*)" class="ni_g_icp ni-video"', resp.text, re.DOTALL)
            if result:
                video_url = result.groupdict().get("video_url")
            else:
                raise Exception("Do not parse!")
            url = 'http://jdx.zjer.cn' + video_url
            resp = req_s.get(url, headers=headers, timeout=__time_out)
            print_time_line()
            print(Fore.GREEN + '访问基地校成功')
            return True
        except Exception as e:
            print_time_line()
            print(Fore.RED + '基地校课程访问失败，错误提示为:' + str(e))
            if i <= __try_time:
                print(f'{Fore.BLUE}重试第{i}次')
            else:
                return


    url = 'http://jdx.zjer.cn/index.php?r=studio/coursecenter/play&sid=600175&kcid=7683&zjid=96609&ksid=96611&fromtype='
    # 或者是 这个？？,好像不是这个 2021年7月12日 22:09:53
    'http://jdx.zjer.cn/index.php?r=studio/pageview/clickview&sid=600175&url=cj1zdHVkaW8vY291cnNlY2VudGVyL2luZm8mc2lkPTYwMDE3NSZpZD03Njgz'


def ke_exp(req_s:requests.sessions.Session):
    for i in range(1, __try_time + 1):
        # 先获取最新播放空间
        try:
            url = 'https://yun.zjer.cn/index.php?r=portal/index/GetModuleHtml2&name=zjStudioCourse'
            resp = req_s.get(url, headers=headers, timeout=__time_out)
            # 具体到某个作者
            result = re.findall('<a href="(?P<syncourse_url>.*?)" target="_blank" class="mgt10">', resp.text, re.DOTALL)
            if result:
                syncourse_url = result[-1]
            else:
                raise Exception("Do not parse!")
            resp = req_s.get(syncourse_url, headers=headers, timeout=__time_out)
            'http://jdx.zjer.cn/index.php?r=curricula/syncourse/info&id=308415'

            result = re.search('style="margin-left: 0;">.+<a href="(?P<infocategory_url>.*?)" class="on course_nav">目录</a>', resp.text, re.DOTALL)
            if result:
                infocategory_url = result.groupdict().get("infocategory_url")
            else:
                raise Exception("Do not parse!")
            url = 'http://ke.zjer.cn' + infocategory_url
            resp = req_s.get(url, headers=headers, timeout=__time_out)

            '<a class=" see mgl20 play_icon" href="/index.php?r=curricula/syncourse/play&kcid=308415&ksid=1557200821" target="_blank"></a>'
            result = re.search("""<a class=" see mgl20 play_icon" href="(?P<syncourse_play_url>.*?)" target="_blank"></a>""", resp.text, re.DOTALL)
            if result:
                syncourse_play_url = result.groupdict().get("syncourse_play_url")
            else:
                raise Exception("Do not parse!")
            # 视频地址
            url = 'http://ke.zjer.cn' + syncourse_play_url
            resp = req_s.get(url, headers=headers, timeout=__time_out)
    
            print_time_line()
            print(Fore.GREEN + '访问直播课成功')
            return True
        except Exception as e:
            print_time_line()
            print(Fore.RED + '直播课成访问失败，错误提示为:' + str(e))
            if i <= __try_time:
                print(f'{Fore.BLUE}重试第{i}次')
            else:
                return


def visit_exp(req_s:requests.sessions.Session):
    for i in range(1, __try_time + 1):
        # 先获取最新播放空间
        try:
            users = [158486, 216333, 134426]  # 建林，盈盈，朱蕾
            url = 'http://yun.zjer.cn/space/index.php?r=space/person/visitor/index&sid='
            for user in users:
                resp = req_s.get(f'{url}{user}', headers=headers, timeout=__time_out)
                time.sleep(1)
            print_time_line()
            print(Fore.GREEN + '访问用户成功')
            return True
        except Exception as e:
            print_time_line()
            print(Fore.RED + '用户访问失败，错误提示为:' + str(e))
            if i <= __try_time:
                print(f'{Fore.BLUE}重试第{i}次')
            else:
                return





'http://yun.zjer.cn/index.php?r=space/person/index&sid=158486'  # 陈建林
'http://yun.zjer.cn/index.php?r=space/person/index&sid=134426' # , '朱蕾'
'http://yun.zjer.cn/index.php?r=space/person/index&sid=216333'  # , '林盈盈'
'http://yun.zjer.cn/space/index.php?r=space/person/visitor/index&sid=134426'


def act_exp():
    user_all = read_user_data()
    for user in user_all:
        req_session = test_user_login(user['account'], user['password'])
        jdx_exp(req_session)   # 基地校没分？？
        ke_exp(req_session)
        visit_exp(req_session)

def act_login():
    user_all = read_user_data()
    for user in user_all:
        req_session = test_user_login(user['account'], user['password'])

if __name__ == '__main__':
    # 类，实例化 login..  jdx
    schedule.every(1).minute.do(print_time_line, pref='Heartbeat:')
    schedule.every(61).to(71).minutes.do(act_login, identify_path='student_info.txt', action='login_jdx')
    act_exp()
    schedule.every().day.at("09:05").do(act_exp)
    while True:
        schedule.run_pending()
        time.sleep(1)
import requests
import json
import argparse
import time


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user", help="用户名/手机号码")
parser.add_argument("-p", "--password", help="密码")
parser.add_argument("-s", "--silence", help="静默运行", action="store_true")
args = parser.parse_args()

user = '' if args.user is None else args.user
pwd = '' if args.password is None else args.password
if user == '' or pwd == '':
    user = input('请输入用户名/手机号码:')
    pwd = input('请输入密码:')
url = 'http://10.131.7.37/ac_portal/login.php'
try:
    data = f'opr=pwdLogin&userName={user}&pwd={pwd}&rememberPwd=0'
    head = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    resp = requests.post(url, data, headers=head).text
    # resp = resp.content.decode('utf-8').replace("'", '"')
    # print(json.loads(resp)['msg'])
    time.sleep(2)
    with open (f"./school_auto_login-{time.strftime('%Y%m%d',time.localtime(time.time()))}.log", 'a+') as f:
        f.write(f"-------------{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}------------->\n")
        f.write(resp + '\n')
        print('写入日志成功...')
    if not args.silence:
        input('请手动关闭')
except Exception as e:
    print(str(e))
from time import sleep
import requests
import pandas as pd


data = pd.read_excel('data.xls', dtype=str)
table_header = ["身份证号","学生姓名","学籍辅号","语文等第","数学等第","外语等第","政治等第","历史等第","地理等第",
                "物理等第","化学等第","生物等第","技术等第","通用技术"]
for i,col_header in enumerate(table_header, start=1):
    data.insert(i, col_header, '')
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # 'Host': '192.168.156.25:8013',
    'Origin': 'http://192.168.156.25:8013',
    'Referer': 'http://192.168.156.25:8013/admin/scores/xkzzscores.htm',
    'Cookie': 'ASP.NET_SessionId=fd0hem4zfumlh2nulc4tgfrt; MEM_NO=xq27; MEM_NAME=%E7%93%AF%E6%B5%B7; MEM_LOGINIP=10.10.4.185; appid=febfe360c21fde1170b6927b94026d81',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}
url = "http://192.168.156.25:8013/admin/ashx/scores.ashx?action=xkzzsearch"

for i in range(len(data)):
    print("开始爬取%s的成绩......" % data.iloc[i, 0])
    response = requests.post(url, {'name':data.iloc[i, 0]}, headers=headers)
    json_data = response.json()
    # json_data = _test_ret_json
    if json_data['total'] >= 1:
        kmdd = list(json_data['rows'][0].values())
        for j in range(1, 15): 
            data.iloc[i, j] =  kmdd[j]
        print(f'第 {i+1}/{len(data)} {data.iloc[i, 1]}同学的成绩为：')
        print(*table_header[3:])
        print(*[f"{km:^8s}" for km in kmdd[3:]])
    else:
        print(f'查询不到 {data.iloc[i, 0]} 同学的成绩。')
    print("*" * 100)
    sleep(0.3)

print("已全部查询完毕，正在导出到csv......")
data["ID"] = data["ID"].apply(lambda x: "\t" + x)
data["学籍辅号"] = data["学籍辅号"].apply(lambda x: "\t" + x)

data.index += 1
data.to_csv('grade_out.csv')
print("导出完毕.")

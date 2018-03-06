"""
 -*- coding: utf-8 -*-
 @author: Kaijian Liu
 @1email:1114889770@qq.com
"""

import requests
import time
from bs4 import BeautifulSoup
import codecs


maxtry=0  #记录重试次数
f = codecs.open('profile.txt', 'r', encoding='utf-8')  #读取配置文件，包含账户及密码
line=f.readline()
f.close()

username = line.split()[0] #你的用户名
password = line.split()[1]  #你的密码
data = {'username': username, 'password':password}

flag = True
day_now = time.localtime(time.time()).tm_mday
f = codecs.open('logging.txt', 'r', encoding='utf-8')
lines = f.readlines()
f.close()
#######更换账户登陆时，最好清除以前账户的日志信息
try:  #如果第一次使用可能没有签到记录
	day_log = int(lines[-1].split()[0].split('-')[-1])
except:
	day_log=33

if day_now == day_log:
    print(username+'今天签到过了哦')
    flag = False

#封装头信息，伪装成浏览器
headers = {
    'Connection': 'Keep-Alive',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3355.4 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'www.nexushd.org',
    'Origin': 'http://www.nexushd.org',
    'Referer': 'http://www.nexushd.org/login.php'
}

cookies = {'Cookie':'c_secure_ssl=bm9wZQ%3D%3D'}
session =requests.session()  #创建会话

while flag:

    url = 'http://www.nexushd.org/takelogin.php'  #登陆界面
    a = session.post(url=url, cookies=cookies, headers=headers, data=data)
    time.sleep(2)

    url2 = 'http://www.nexushd.org/signin.php'  #签到界面
    b = session.get(url=url2, headers=headers)
    time.sleep(2)

    url3 = 'http://www.nexushd.org/signin.php?'
    qiandao = {'action':'post','content':'lalala2333'} #签到信息随便填，lalala2333
    r = session.post(url=url3, headers=headers, data=qiandao)
    r = BeautifulSoup(r.content,'lxml')
    message = r.find_all('a',{'href':"signin.php"})[0].contents[0]
    if message == '已签到': #如果已经签到
        f = codecs.open('logging.txt', 'a', encoding='utf-8')
        str= time.strftime('%Y-%m-%d  %H:%M:%S',time.localtime(time.time())) +'-----签到成功'+'\n'
        f.write(str)  #记录日志信息到日志文件
        f.close()
        print(r.find_all('span',{'class':'medium'})[0].getText())
        print(r.find_all('td',{'class':'text'})[-1].getText().split('。')[0])
        break
    if maxtry<30:
        print('签到失败，第'+str(maxtry)+'次重试')
        time.sleep(5)
    else:
        print("自动签到失败，请手动签到，或者检查网络连接")
        break





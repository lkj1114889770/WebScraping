import requests
import json
import csv
from twilio.rest import Client
import time

#以下xxxx部分都需要根据自己的Twilio账户信息进行配置
SID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
client = Client(SID,TOKEN)
To = 'xxxxxxxxxxxxxxxxxxxx'
From = 'xxxxxxxxxxxxxxxxxx'
Body = u'啦啦啦啦啦'

#messeage = client.messages.create(to=To,from_=From,body=Body)

url = 'https://kyfw.12306.cn/otn/leftTicket/queryX?leftTicketDTO.train_date=2017-10-08&leftTicketDTO.from_station=YTG&leftTicketDTO.to_station=HZH&purpose_codes=ADULT'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'kyfw.12306.cn',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3218.0 Safari/537.36',

}
f_cookies = open('cookies.txt', 'r')
cookies = {}
for line in f_cookies.read().split(';'):
    name, value = line.strip().split('=', 1)
    cookies[name] = value


while True:
    a = requests.get(url, cookies=cookies,headers=headers,verify = False)
    while (a.status_code !=200):
        time.sleep(10)
        a = requests.get(url, cookies=cookies, headers=headers, verify=False)
    data = json.loads(a.content.decode('utf-8','ignore'))
    train_infos = data['data']['result']
    train_infos_csv=[]
    infos = train_infos
    for info in infos:
        train_infos_csv.append((info.replace('|',','))+'\n')
    f = open('train_infos.csv','w')
    for info in train_infos_csv:
        f.write(info)

    f.close()
    csv_reader = csv.reader(open('train_infos.csv'))
    HSR_infos=[]
    for info in csv_reader:
        if('G' in info[3]):
            HSR_infos.append(info)
        elif('D' in info[3]):
            HSR_infos.append(info)

    Ticket_avaliable=''
    for info in HSR_infos:
        if(info[-6] != u'无'):
            Ticket_avaliable=Ticket_avaliable + info[3] +','
    Body=u'这些车次还有票' + Ticket_avaliable
    if(Ticket_avaliable ==''):
        print(u'好悲伤，没票了')
        time.sleep(5)
    else:
        print(Body)
        messeage = client.messages.create(to=To, from_=From, body=Body)
        time.sleep(600)
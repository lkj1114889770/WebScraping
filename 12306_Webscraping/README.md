---
title: 12306车次查询与短信提醒
date: 2017-10-02 10:33:05
tags:
	- 爬虫
---
正值国庆，不想出去玩看人，也无法在实验室知识的海洋里遨游整个假期，就干脆回家，无奈却买不到回来的票（国庆真是堪比春运啊），只能买到途径站的票。12306官方给的自动刷新车票的系统太渣，经常自己卡死停掉，因此想到用python爬取12306网站车票信息，利用Twilio在有票的情况下短信通知我。

![](https://i.imgur.com/DzxBB97.png)

<!-- more -->

首先打开12306的查票页面[https://kyfw.12306.cn/otn/leftTicket/init ](https://kyfw.12306.cn/otn/leftTicket/init )输入出发地和目的地进行搜索。
下面就是常见的套路，对于谷歌浏览器按F12打开开发者工具，获取查询的时候的数据信息。按下查询之后，可以发现有两个数据请求：

![](https://i.imgur.com/fGEXVjb.png)

显然第二个请求返回数据含有我们需要的车次信息，因此根据第二个请求的header来封装我们requests.get时候的请求包，以及如何封装cookies也可见之前的[爬虫博客](http://blog.lkj666.top/2017/08/08/也看战狼2：爬取豆瓣影评做词云/#more)。


	url = 'https://kyfw.12306.cn/otn/leftTicket/queryX?leftTicketDTO.train_date=2017-10-08&leftTicketDTO.from_station=YTG&leftTicketDTO.to_station=HZH&purpose_codes=ADULT'
	headers = {
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.9',
	    'Accept-Language': 'zh-CN,zh;q=0.9',
	    'Host': 'kyfw.12306.cn',
	    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3218.0 Safari/537.36',
	}

由于12306网站还有SSL验证，所以用常规的方法去get数据都会有SSLError，最简单的处理方式就是直接忽略这个验证。

	 a = requests.get(url, cookies=cookies,headers=headers,verify = False)

12306网站在访问的时候经常有时候请求不到数据，这个时候需要进行判别，以防止后续处理信息报错，有计算机网络知识就知道，正常的http response的状态code就是会返回200，可以据此来判别。

    while (a.status_code !=200):
        time.sleep(10)
        a = requests.get(url, cookies=cookies, headers=headers, verify=False)

对返回的车次信息进行查看，返回的信息类似于jason格式的文件，车次信息包含在里面。

![](https://i.imgur.com/PESBfPR.png)

通过json.load进行读取后返回字典格式文件，取出其中的车次此案次，存为csv文件后用excel打开，以便更加直观地分析。

![](https://i.imgur.com/PpUZ7Qk.png)

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

下面需要取出所需要的信息，我要的是高铁或者动车的二等座，再进行一次过滤：

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

上面的client.messages.create就是发送短信模块，需要用到Twilio，首先需要到Twilio官方网站注册之后账号，有账户的SID 和TOKEN后进行配置，就能发送了

	SID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
	TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
	client = Client(SID,TOKEN)
	To = '+86xxxxxxxxxxxxxxx'
	From = 'xxxxxxxxxxxxxx'
	Body = u'啦啦啦啦啦'
	messeage = client.messages.create(to=To,from_=From,body=Body)

上面的xxxx部分都需要根据自己的账户替换自己的信息。
这样就实现了有票自动提醒，由于Twilio接收短信比较麻烦，所以没法通过短信终止程序，只能在查到票之后先终止运行10分钟，其实可以考虑通过邮件来控制程序，这个还是比较好操作的。
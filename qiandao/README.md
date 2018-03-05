---
title: NHD自动登陆签到脚本
date: 2018-03-05 20:46:38
tags:
	- 爬虫
---
到现在做过很多爬虫的小玩意，今天用爬虫来做一个更实际的东西。学校内部有个电影资源分享网站[NHD](http://www.nexushd.org/index.php)，虽然说是免费下载，但是需要消耗魔力值，魔力值可以通过每天签到获得，连续签到的话每天得到的魔力值数量客观，但是有时候会忘了签到，因此写了一个小程序来实现每天自动登陆NHD并实现自动签到。
<!-- more -->

首先还是老套路，先用浏览器实现一遍登陆以及签到过程，用谷歌浏览器的开发者模式获取这过程中的信息。可以看到首次登陆之后，response的header有set-cookie字段

![](https://i.imgur.com/blGVz73.png)

而后这个服务器返回的set-cookie字段在下一次会话中又出现了

![](https://i.imgur.com/gI5d49F.png)


其实总体思路还是很简单的，与之前的爬虫不同，这次需要用户登陆，所以是POST方法，并将用户名和密码以data参数代入，登陆之后服务器会返回cookie来标识用户。因为http是一种无状态协议，用户首次访问web站点的时候，服务器对用户一无所知。而Cookie就像是服务器给每个来访问的用户贴的标签，而这些标签就是对来访问的客户端的独有的身份的一个标识，这里就如同每个人的身份证一样，带着你的个人信息。而当一个客户端第一次连接过来的时候，服务端就会给他打一个标签，这里就如同给你发了一个身份证，所以之后的访问服务器再带上这个cookie就标识了该账户，具体流程网上找到一张很好的图可以解释。

![](https://images2015.cnblogs.com/blog/997599/201707/997599-20170720145847427-1503464818.png)

这样的话，只需要第一次输入密码，后面浏览器再次访问只要带上这个服务器返回的cookie，服务器就可以知道是该账户在访问，所以python程序也模拟该过程。利用request库中的session对象来创建类似于图中的过程，session对象会保存访问过程中的cookie用于之后对服务器的继续访问。

	url = 'http://www.nexushd.org/takelogin.php'  #登陆界面
	a = session.post(url=url, cookies=cookies, headers=headers, data=data)
	#这里的cookie是浏览器首次访问的使用的cookie，之后服务器
	#设置的cookie会保存在session对象中
	time.sleep(2)
	
	url2 = 'http://www.nexushd.org/signin.php'  #签到界面
    b = session.get(url=url2, headers=headers)
    time.sleep(2)

    url3 = 'http://www.nexushd.org/signin.php?'
    qiandao = {'action':'post','content':'lalala2333'} #签到信息随便填，lalala2333
    r = session.post(url=url3, headers=headers, data=qiandao)

而后就是一个判断是否登陆成功的程序，依然使用BeautifulSoup来解析，得到已签到之后退出循环，并将日志信息记录到日志文件。

	r = session.post(url=url3, headers=headers, data=qiandao)
    r = BeautifulSoup(r.content,'lxml')
    message = r.find_all('a',{'href':"signin.php"})[0].contents[0]
    if message == '已签到': #如果已经签到
        f = codecs.open('logging.txt', 'a', encoding='utf-8')
        str= time.strftime('%Y-%m-%d  %H:%M:%S',time.localtime(time.time())) +'-----签到成功'+'\n'
        f.write(str)  #记录日志信息到日志文件
        f.close()
        break

测试结果：

![](https://i.imgur.com/9KcOc9O.png)

之后我把这个代码挂在自己寝室一直在运行的主机上，就可以保证每天实现签到了。目前来来说，程序没有出现什么问题，所以先记录一下，但是之后长时间运行不知道会怎样，或许得优化，反正先放出来，以后还能改。

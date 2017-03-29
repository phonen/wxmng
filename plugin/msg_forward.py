#!/usr/bin/env python
# coding: utf-8
#####插件说明#####
#post方式转发消息到指定的url中！
import json
import web
import requests
import thread

def run(WXBOT,msg,plugin_name):
	try:
		WXBOT.bot_conf[plugin_name]
	except:
		WXBOT.bot_conf[plugin_name] = ['http://www.vivre.cn/msg_recive.php']

	try:
		for url in WXBOT.bot_conf[plugin_name]:
			data = {
					"msg":msg,
					"bot_id":WXBOT.uuid,
					"account_uin":WXBOT.my_account['Uin']
				}
			thread.start_new_thread(send_msg,(url,data,plugin_name))
	except Exception,e:
		print u'[ERRO]%s插件运行错误--->%s'%(plugin_name,e)

def send_msg(url,data,plugin_name):
	#print url,data
	try:
		r = requests.post(url,data=data)
		result = r.json()
		print u'[INFO] %s插件往%s消息转发结果--->%s,%s'%(plugin_name,r.status_code,result)
	except Exception,e:
		print u'[ERRO] %s插件往%s消息转发发生错误--->%s'%(plugin_name,url,e)
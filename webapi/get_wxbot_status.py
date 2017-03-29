#!/usr/bin/env python
# coding: utf-8
import pyqrcode
import os
import thread
import time
import requests
from traceback import format_exc

def run(web_input,action,bot_list):
	#action ---> http://127.0.0.1/api/*****/  其中×××对应的就是action,通过action字段来实现自定义的操作在下面主程序编写业务逻辑
	#返回格式如下，code目前为200和500，200为正常，500为异常
	#查询当前登录的所有机器人状态
	if action == 'get_wxbot_status':
		try:
			data = []
			for x in bot_list:
				try:
					bot_account_name = x.bot.my_account['NickName']
					bot_account_uin = x.bot.my_account['Uin']
					bot_conf        = x.bot.bot_conf
					bot_contact_num = len(x.bot.contact_list)
					bot_group_num = len(x.bot.group_list)
				except Exception,e:
					bot_account_name = ''
					bot_account_uin  = ''
					bot_conf         = ''
					bot_contact_num  = ''
					bot_group_num	= ''
					print e,bot_account_name
				try:
					temp = {
					    'bot_start_time':x.bot_start_time,
						'bot_id':x.bot_id,
						'login_qr':'/static/temp/'+str(x.bot_id)+'.png',
						'bot_status':x.bot.status,
						'bot_account_name':bot_account_name,
						'bot_account_uin':bot_account_uin,
						'bot_conf':bot_conf,
						'bot_contact_num':bot_contact_num,
						'bot_group_num':bot_group_num
					}
					data.append(temp)
				except:
					continues
			return {'code':200,'error_info':'','data':data}
		except Exception,e:
			return {'code':500,'error_info':str(format_exc()),'data':''}
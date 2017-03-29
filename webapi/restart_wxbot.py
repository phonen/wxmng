#!/usr/bin/env python
# coding: utf-8
import pyqrcode
import os
import thread
import time
import requests

def run(web_input,action,bot_list):
	#action ---> http://127.0.0.1/api/*****/  其中×××对应的就是action,通过action字段来实现自定义的操作在下面主程序编写业务逻辑
	#返回格式如下，code目前为200和500，200为正常，500为异常
	#重新启动某一个机器人
	if action == 'restart_wxbot':
		try:
			bot_id = web_input['bot_id']
			try:
				not_care_login_status = int(web_input['not_care_login_status'])
			except:
				not_care_login_status = 0
			#print not_care_login_status
			for x in bot_list:
				if x.bot_id == bot_id and (x.bot.status == 'loginout' or not_care_login_status==1):
					thread.start_new_thread(x.bot.run,())
					time.sleep(3)
					x.bot_id = x.bot.uuid
					x.login_qr = '/static/temp/'+str(x['bot'].uuid)+'.png'
					data = {
							'bot_id':x.bot_id,
							'login_qr':x.login_qr
					}
					return {'code':200,'error_info':'','data':data}
			return {'code':500,'error_info':'bot_id not found or bot_status not loginout!','data':''}
		except Exception,e:
			return {'code':500,'error_info':str(e),'data':''}
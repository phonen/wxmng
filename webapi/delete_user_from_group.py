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

	#通过uid发送文件消息
	if action == 'delete_user_from_group':
		try:
			bot_id = web_input['bot_id']
			uname    = web_input['uname']
			gid    = web_input['gid']
			for x in bot_list:
				if x.bot_id == bot_id:
					#远程图片to本地图片
					data = x.bot.delete_user_from_group(uname,gid)
					return {'code':200,'error_info':'','data':data}
			return {'code':500,'error_info':'bot_id not found!!','data':''}
		except Exception,e:
			return {'code':500,'error_info':str(e),'data':''}
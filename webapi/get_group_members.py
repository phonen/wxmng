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

	#获取当前登录的微信账号群聊中的群成员信息
	if action == 'get_group_members':
		try:
			bot_id = web_input['bot_id']
			for x in bot_list:
				if x.bot_id == bot_id:
					data = {
						'group_members':x.bot.group_members
						}
					return {'code':200,'error_info':'','data':data}
			return {'code':500,'error_info':'bot_id not found!!','data':''}
		except Exception,e:
			return {'code':500,'error_info':str(e),'data':''}

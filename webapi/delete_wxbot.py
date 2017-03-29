#!/usr/bin/env python
# coding: utf-8
import json

def run(web_input,action,bot_list):
	#action ---> http://127.0.0.1/api/*****/  其中×××对应的就是action,通过action字段来实现自定义的操作在下面主程序编写业务逻辑
	#返回格式如下，code目前为200和500，200为正常，500为异常
	#获取当前登录的微信帐号的配置信息--插件配置为主！！
	if action == 'delete_wxbot':
		try:
			bot_id = web_input['bot_id']
			i = 0 
			del_index = None
			for x in bot_list:
				if x.bot_id == bot_id:
					del_index = i 
					#更改状态，等待信息处理线程退出
					if x.bot.status == 'loginsuccess':
						x.bot.status = 'wait4loginout'
					x.join()
					break
				i = i + 1
			if del_index != None:
				del bot_list[del_index]
				return {'code':200,'error_info':'','data':True}
			return {'code':500,'error_info':'bot_id not found!','data':''}
		except Exception,e:
			return {'code':500,'error_info':str(e),'data':''}
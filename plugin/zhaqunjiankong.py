#!/usr/bin/env python
# coding: utf-8
#####插件说明#####
#炸群监控插件！！通过匹配消息中的敏感词数量来自动踢出某些群内的捣乱分子
import json
import web
import re
import os

def run(WXBOT,msg,plugin_name):
	try:
		WXBOT.bot_conf[plugin_name]
	except:
		WXBOT.bot_conf[plugin_name] = {
		    'switch' : True,      #防炸群功能开关
		    'black_keys' : [u'加我'] ,   #炸群恶意关键词匹配
		    'max_black_keys' : 2 ,  #命中几个关键词后踢人
		    'max_text_length': 80000,  #消息允许的最大长度
		    'badgay_message' : u'%s由于违反群内消息发送规定，已被踢出此群，请大家注意遵守群内秩序!',  #炸群踢人消息
		    'admin_account_list' : [u'小V',u'A0淘宝优惠助手-悠悠']  #有踢人权限的账号列表
		}
		return

	if WXBOT.bot_conf[plugin_name]['switch'] == True and (msg['msg_type_id'] == 3 and  msg['content']['type'] == 0):
		#那些炸群的捣乱分子统统干掉
		key_hit = 0	 
		for x in WXBOT.bot_conf[plugin_name]['black_keys']:
			if msg['content']['data'].find(x) >=0:
				key_hit = key_hit + 1
		if (key_hit >= WXBOT.bot_conf[plugin_name]['max_black_keys']) or (len(msg['content']['data']) >WXBOT.bot_conf[plugin_name]['max_text_length'] ):
			#关键词命中够了，就自动踢出这人
			WXBOT.delete_user_from_group(msg['content']['user']['name'],msg['user']['id'])
			#拼接消息并群内通知
			badgay_message = WXBOT.bot_conf[plugin_name]['badgay_message']%(msg['content']['user']['name'])
			WXBOT.send_msg_by_uid(badgay_message,msg['user']['id'])			
			#尝试记录数据到数据库中-----没写！！！需要得话参考groupmanage里面得代码
			print u'[INFO] 炸群自动踢人成功，%s---->%s\n%s'%(msg['user']['name'],msg['content']['user']['name'],msg['content']['data'])

	if WXBOT.bot_conf[plugin_name]['switch'] == True and (msg['msg_type_id'] == 3 and msg['content']['type'] == 0):
		try:
			#print json.dumps(msg,indent=4)
			if msg['content']['detail'][0]['type'] == 'at' and msg['content']['user']['name'] in WXBOT.bot_conf[plugin_name]['admin_account_list']:  
				#print json.dumps(msg,indent=4)
				if msg['content']['desc'] == u'踢':
					print u'[INFO] 收到管理命令：%s-->踢掉-->%s'%(msg['user']['name'],msg['content']['detail'][0]['value'])
					WXBOT.delete_user_from_group(msg['content']['detail'][0]['value'],msg['user']['id'])
					badgay_message = WXBOT.bot_conf[plugin_name]['badgay_message']%(msg['content']['detail'][0]['value'])
					WXBOT.send_msg_by_uid(badgay_message,msg['user']['id'])		
		except Exception,e:
			pass
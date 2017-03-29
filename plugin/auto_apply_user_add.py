#!/usr/bin/env python
# coding: utf-8
#####插件说明#####
#自动通过好友请求，并参与相应的措施
import json
import web
import re
import os

def run(WXBOT,msg,plugin_name):
	try:
		WXBOT.bot_conf[plugin_name]
	except:
		WXBOT.bot_conf[plugin_name] = {
		    'switch':True,  #自动通过好友请求开关
		    'welcome_msg':u'欢迎加我好友!', #加好友的欢迎消息 
		    
		    'switch_group_auto':False,  #自动邀请进群开关
		    'groupname':u'小黄牛XXX群'  #必须保存在通讯录中
		}

	if  WXBOT.bot_conf[plugin_name]['switch'] == True and msg['msg_type_id'] == 37:
		#自动通过好友请求
		WXBOT.apply_useradd_requests(msg['content']['data'])
		#更新下通讯录，然后就可以username，不然只能用uid。发发发消息了。
		#WXBOT.get_contact()

		WXBOT.send_msg_by_uid(WXBOT.bot_conf[plugin_name]['welcome_msg'],msg['content']['data']['UserName'])   #主动发送文本消息
		#WXBOT.send_file_msg_by_uid(os.path.join(os.getcwd(),'temp','图片名'),msg['content']['data']['UserName'])   #主动发送图片消息    
		if WXBOT.bot_conf[plugin_name]['switch_group_auto'] == True:
		    WXBOT.add_friend_to_group(msg['content']['data']['UserName'],WXBOT.bot_conf[plugin_name]['groupname'])  #自动拉他进群
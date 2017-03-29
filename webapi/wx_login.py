#!/usr/bin/env python
# coding: utf-8
import Lib.wxbot
import pyqrcode
import os
import thread
import time
import json
import requests
import threading
from traceback import format_exc

def run(web_input,action,bot_list):
    #action ---> http://127.0.0.1/api/*****/  其中×××对应的就是action,通过action字段来实现自定义的操作在下面主程序编写业务逻辑
    #返回格式如下，code目前为200和500，200为正常，500为异常
    #{'code':200,'error_info':'','data':''}

    #登陆微信账号
    if action == 'wx_login':
        try:
            bot_conf = json.loads(web_input['bot_conf'])
        except Exception,e:
            print '[INFO] Web WeChat load_emtry_conf -->',e
            bot_conf = {}
        try:
            #启动机器人
            temp = weixin_bot()
            temp.start()
            bot_list.append(temp)
            time.sleep(5)
            temp.bot.bot_conf = bot_conf
            temp.bot_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data = {
                'bot_id':temp.bot_id,
                'login_qr':'/static/temp/'+str(temp.bot_id)+'.png',
                'bot_start_time':temp.bot_start_time 
            }
            return {'code':200,'error_info':'','data':data}
        except Exception,e:
            return {'code':500,'error_info':str(e),'data':''}

class weixin_bot(threading.Thread):
    # 重写父类run()方法
    def run(self):
        self.bot = ReWxbot()
        self.bot.DEBUG = True
        bot_run_thread = thread.start_new_thread(self.bot.run,())
        time.sleep(3)
        self.bot_id = self.bot.uuid
        self.login_qr = '/static/temp/'+str(self.bot.uuid)+'.png'

            
class ReWxbot(Lib.wxbot.WXBot):

    def handle_msg_all(self, msg):
        #载入插件系统，插件支持动态修改！修改后实时生效，无需重启程序！
        for filename in os.listdir("plugin"):
            try:
                if not filename.endswith(".py") or filename.startswith("_"):
                    continue
                pluginName=os.path.splitext(filename)[0]
                plugin=__import__("plugin."+pluginName, fromlist=[pluginName])
                reload(plugin)
                plugin.run(self,msg,pluginName)
            except Exception,e:
                print u'[ERRO] 插件%s运行错误--->%s'%(filename,e)
                
    def gen_qr_code(self,ts):
        string = 'https://login.weixin.qq.com/l/' + self.uuid
        qr = pyqrcode.create(string)
        qr.png(os.path.join(os.getcwd(),'static','temp',str(self.uuid)+'.png'), scale=8)

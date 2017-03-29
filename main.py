#!/usr/bin/env python
# coding: utf-8
import web
import json
import requests
import os
from traceback import format_exc
import webbrowser
############################################################################################################################################################################
#webapi代码区
#数据库地址,WEB相关配置
web_db  = web.database(dbn="sqlite", db=os.path.join(os.getcwd(),'data','weixin.db'))
render = web.template.render('webui_templates')

class index: 
    def GET(self):
        if web.ctx.session.logged_in  == True  :
            return render.index()
        else:
            raise web.seeother('/login.html')

class login: 
    def GET(self):
        return render.login()

    def POST(self):
        try:
            username=web.input()['username']
            password=web.input()['password']
            if username == 'admin' and password =='admin':
                web.ctx.session.logged_in = True
                raise web.seeother('/index.html')
            return render.login()
        except:
            return render.login()
            
#web界面相关代码区域
class webui:
    def GET(self,action):
        if web.ctx.session.logged_in  != True :
            raise web.seeother('/login.html')
        if action == 'wx_login':
            data = requests.get('http://127.0.0.1:8080/api/wx_login/').json()
            return render.wx_login(data) 
            
        if action == 'bot_list':
            data = requests.get('http://127.0.0.1:8080/api/get_wxbot_status/').json()
            return render.bot_list(data) 
            
        if action == 'get_bot_conf':
            bot_id = web.input()['bot_id']    
            data = requests.get('http://127.0.0.1:8080/api/get_bot_conf/?bot_id=%s'%(bot_id)).json()
            bot_conf = json.dumps(data['data']['bot_conf'],ensure_ascii=False,indent=4)
            return render.get_bot_conf(bot_id,bot_conf)
        
        if action == 'get_contact_list':
            bot_id = web.input()['bot_id']    
            data = requests.get('http://127.0.0.1:8080/api/get_contact_list/?bot_id=%s'%(bot_id)).json()
            return render.get_contact_list(bot_id,data) 
            
        if action == 'get_group_list':
            bot_id = web.input()['bot_id']    
            data = requests.get('http://127.0.0.1:8080/api/get_group_list/?bot_id=%s'%(bot_id)).json()
            group_members = requests.get('http://127.0.0.1:8080/api/get_group_members/?bot_id=%s'%(bot_id)).json()['data']['group_members']
            group_list = data['data']['group_list']
            new_group_list = []
            for temp in group_list:
                try:
                    temp['MemberNums'] = len(group_members[temp['UserName']])
                except:
                    temp['MemberNums'] = 0 
                new_group_list.append(temp)
            data['data']['group_list'] = new_group_list
            return render.get_group_list(bot_id,data) 
            
        if action == 'get_group_member_list':
            bot_id = web.input()['bot_id']    
            gid    = web.input()['gid']
            group_members = requests.get('http://127.0.0.1:8080/api/get_group_members/?bot_id=%s'%(bot_id)).json()['data']['group_members']
            return render.get_group_member_list(bot_id,gid,group_members[gid])     
            
    def POST(self,action):
        if web.ctx.session.logged_in  != True  :
            raise web.seeother('/login.html')
            
        if action == 'delete_wxbot':
            bot_id = web.input()['bot_id']    
            data = requests.get('http://127.0.0.1:8080/api/delete_wxbot/?bot_id=%s'%(bot_id)).json()
            return '{"statusCode":"200","message":"操作成功","navTabId":"bot_list"}'
            
        if action == 'update_bot_conf':
            bot_id = web.input()['bot_id']    
            bot_conf = web.input()['bot_conf']
            post_data = {'bot_id':bot_id,'bot_conf':bot_conf}
            data = requests.post('http://127.0.0.1:8080/api/update_bot_conf/?bot_id=%s'%(bot_id),data=post_data).json()
            return '{"statusCode":"200","message":"操作成功"}'
            
#webapi相关代码区域，此部分代码为动态加载，每个api接口在webapi目录中对应一个文件
#一个api同时支持GET和POST方式调用，效果相同            
class api:
    def GET(self,action):
        try:
            plugin = __import__("webapi."+action, fromlist=[action])
            reload(plugin)
            result =  plugin.run(web.input(),action,bot_list)
        except Exception,e:
            result = {'code':500,'error_info':str(format_exc()),'data':''}
        web.header('Content-Type','application/json')
        return json.dumps(result,indent=4)

    def POST(self,action):
        try:
            plugin = __import__("webapi."+action, fromlist=[action])
            reload(plugin)
            result =  plugin.run(web.input(),action,bot_list)
        except Exception,e:
            result = {'code':500,'error_info':str(format_exc()),'data':''}
        web.header('Content-Type','application/json')
        return json.dumps(result,indent=4)

class not_found:
    def GET(self,url):
        raise web.seeother('/login.html')

def web_thread():
    web.config.debug = False

    urls = (
        '/index.html','index',
        '/login.html','login', 
        
        '/webui/(.+)/','webui',        
        '/api/(.+)/','api',
        
        '(.+)','not_found'
    )
    
    app = web.application(urls, globals())  
    #定义seesion模型
    store   = web.session.DBStore(web_db, 'sessions') 
    session = web.session.Session(app, store, initializer = {
            "logged_in": False
            })

    #hook seesion到所有的子应用
    def session_hook():
        web.ctx.session = session
    app.add_processor(web.loadhook(session_hook))
    #启动web应用
    app.run()

############################################################################################################################################################################

if __name__ == '__main__':

    #机器人列表
    bot_list = []
    #启动web控制台
    webbrowser.open_new_tab('http://127.0.0.1:8080/login.html')
    #启动web线程
    web_thread()
    
    
    
    
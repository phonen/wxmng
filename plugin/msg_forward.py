#!/usr/bin/env python
# coding: utf-8
#####插件说明#####
# post方式转发消息到指定的url中！
import json
import web
import requests
import re
import random
import os
import time

def run(WXBOT, msg, plugin_name):
    try:
        WXBOT.bot_conf[plugin_name]
    except:
        WXBOT.bot_conf[plugin_name] = {
            'switch': True,
            'tuling_key':'0c68515ebcb2920ea3844d4f8fba60fe',
            'alimama_siteid': '15574862',
            'alimama_adzoneid': '59576937',
            'alimama_sign_account': 'ca387a0f250083076b1b2168c824881f',
            'site_url':'http://13bag.com/',
            'message_send_with_coupons': u'发现优惠券啦！复制这条信息%s，打开【手机淘宝】可领取本群专属手机优惠劵【%s元】在下单购买！如果无法领取说明代金券已经领取完！',
            'message_send_with_fanli': u'复制本内容%s,打开【手机淘宝】下单并确认收货后将订单号私聊我，可以领取商家红包【%s元】！有问题可以私聊咨询我！',
            'message_search_fail': u'没有相关优惠，换个试试吧～'
        }

    if WXBOT.bot_conf[plugin_name]['switch'] == True and (msg['msg_type_id'] == 3 and msg['content']['type'] == 0):
        try:
            print WXBOT.my_account['UserName']
            print WXBOT.my_account['NickName']
            print msg['content']['detail'][0]['value']
            if msg['content']['detail'][0]['type'] == 'at' and msg['content']['detail'][0]['value'] == WXBOT.my_account['NickName']:
                print '[INFO] Start anaysis Message!'

                # 匹配查询命令，并找到对应关键词商品回复
                search_pattern = re.compile(u"^(买|找|帮我找|有没有|我要买|宝宝要|宝宝买)\s?(.*?)$")
                Command_result = search_pattern.findall(msg['content']['desc'])
                if len(Command_result) == 1:
                    skey = Command_result[0][1]
                    print u'[INFO] TBK命中查询命令，关键词-->%s' % (skey)
                    #result, data = A_MAMA.search_item_info_by_key_use_queqiao(skey)
                    #send_search_result_to_uid(WXBOT, A_MAMA, data, msg, skey, '', plugin_name)
                    # 模糊匹配url提取商品id
                else:
                    search_url_pattern = re.compile(u"[a-zA-z]+://[^\s]*")
                    Command_result = search_url_pattern.findall(msg['content']['desc'])
                    if len(Command_result) > 0:
                        iid = search_iid_from_url(Command_result[0])
                        print u'[INFO] LOG-->Command_result:%s' % (str(Command_result))
                        if iid != '':
                           print u'[INFO] TBK发现商品ID-->%s' % (iid)
                        result, data = A_MAMA.search_item_info_by_iid(iid)
                        send_search_result_to_uid(WXBOT, A_MAMA, data, msg, '', iid, plugin_name)
                    else:

                        WXBOT.send_msg_by_uid(
                            '@' + msg['content']['user']['name'] + ': ' + tuling_auto_reply(msg['user']['id'], msg['content']['data'],
                                                                      WXBOT.bot_conf[plugin_name]['tuling_key']),
                            msg['user']['id'])

        except Exception, e:
            print str(e)
            pass

    if WXBOT.bot_conf[plugin_name]['switch'] == True and (msg['msg_type_id'] == 4 and msg['content']['type'] == 0):
        try:
            print '[INFO] Start anaysis Message1!'
            # 匹配查询命令，并找到对应关键词商品回复
            search_pattern = re.compile(u"^(买|找|帮我找|有没有|我要买|宝宝要|宝宝买)\s?(.*?)$")
            Command_result = search_pattern.findall(msg['content']['data'])
            if len(Command_result) == 1:
                skey = Command_result[0][1]
                print u'[INFO] TBK命中查询命令，关键词-->%s' % (skey)
                # result, data = A_MAMA.search_item_info_by_key_use_queqiao(skey)
                # send_search_result_to_uid(WXBOT, A_MAMA, data, msg, skey, '', plugin_name)
                # 模糊匹配url提取商品id
            else:
                search_url_pattern = re.compile(u"[a-zA-z]+://[^\s]*")
                Command_result = search_url_pattern.findall(msg['content']['data'])
                if len(Command_result) > 0:
                    # iid = search_iid_from_url(Command_result[0])
                    print u'[INFO] LOG-->Command_result:%s' % (str(Command_result))
                    # if iid != '':
                    #    print u'[INFO] TBK发现商品ID-->%s' % (iid)
                    # result, data = A_MAMA.search_item_info_by_iid(iid)
                    # send_search_result_to_uid(WXBOT, A_MAMA, data, msg, '', iid, plugin_name)
                else:
                    print u'发送！'
                    WXBOT.send_msg_by_uid(tuling_auto_reply(msg['user']['id'],msg['content']['data'],WXBOT.bot_conf[plugin_name]['tuling_key']),msg['user']['id'])
        except Exception, e:
            print str(e)
            pass

def tuling_auto_reply(uid, msg, tuling_key):
    if tuling_key:
        url = "http://www.tuling123.com/openapi/api"
        user_id = uid.replace('@', '')[:30]
        body = {'key': tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
        r = requests.post(url, data=body)
        respond = json.loads(r.text)
        result = ''
        if respond['code'] == 100000:
            result = respond['text'].replace('<br>', '  ')
        elif respond['code'] == 200000:
            result = respond['url']
        elif respond['code'] == 302000:
            for k in respond['list']:
                result = result + u"【" + k['source'] + u"】 " + \
                         k['article'] + "\t" + k['detailurl'] + "\n"
        else:
            result = respond['text'].replace('<br>', '  ')

        print '    ROBOT:', result
        return result
    else:
        return u"知道啦"


def get_order(site_url,proxywx, oid):
    post_data = {'oid': oid, 'proxywx': proxywx}
    print post_data
    post_url = site_url + '?g=Tbkqq&m=WxAi&a=order_json'
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f


def get_taoke_link(site_url,group, proxywx, msg, debug):
    post_data = {'group': group, 'proxywx': proxywx, 'msg': msg, 'debug': debug}
    print post_data
    post_url = site_url + '?g=Tbkqq&m=WxAi&a=taoke_info'
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f


def get_taoke_link_by_proxyid(site_url,proxyid, msg):
    post_data = {'proxyid': proxyid, 'msg': msg}
    print post_data
    post_url = site_url + '?g=Tbkqq&m=WxAi&a=taoke_info_by_proxyid'
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f


def save_proxy(site_url,proxywx, msg):
    post_data = {'proxywx': proxywx, 'msg': msg}
    post_url = site_url + '?g=Tbkqq&m=Ai&a=save_link'
    r = requests.post(post_url, post_data)
    r.encoding = 'utf-8'
    f = r.text.encode('utf-8')
    return f


def search_iid_from_url(x):
	#从消息中提取的url来进行iid的提取，这个函数代扩容！！
	search_iid_pattern =  re.compile(u"(http|https)://(item\.taobao\.com|detail\.tmall\.com)/(.*?)id=(\d*)")
	search_iid_pattern_2 = re.compile(u'(http|https)://(a\.m\.taobao\.com)/i(\d*)\.htm')
	r = requests.get(x,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'})
	iid = ''
	temp = search_iid_pattern.findall(r.url)
	if len(temp)==0:
		try:
			iid = search_iid_pattern.findall(r.content)[0][3]
		except:
			try:
				iid = search_iid_pattern_2.findall(r.content)[0][2]
			except:
				pass
	else:
		iid = temp[0][3]
	return iid


def send_search_result_to_uid(WXBOT,A_MAMA,data,msg,skey=None,iid=None,plugin_name=None):
	#模糊匹配中，如果匹配到查询命令会调用此函数
	if data['data']['pageList'] != None:
		item_info = data['data']['pageList'][random.randint(0,len(data['data']['pageList'])-1)]
		item_info['title'] = re.sub(u'<(.*?)>','',item_info['title'])
		result,sclick_data = A_MAMA.create_auction_code_with_tkl(item_info['auctionId'],WXBOT.bot_conf[plugin_name]['alimama_siteid'],WXBOT.bot_conf[plugin_name]['alimama_adzoneid'],item_info)
		send_item_pic_to_uid(WXBOT,item_info,msg)
		time.sleep(0.5)
		try:
		    #尝试获取2合1的淘口令,整合代金券
			sclick_data['data']['couponLinkTaoToken']
			WXBOT.send_msg_by_uid(WXBOT.bot_conf[plugin_name]['message_send_with_coupons']%(sclick_data['data']['couponLinkTaoToken'],item_info['couponAmount']),msg['user']['id'])
		except:
			time.sleep(0.5)
			#没找到代金券，开启返利模式
			fanli_fee = int(int(item_info['tkCommFee'])*0.4)
			fanli_fee = (str(fanli_fee) if fanli_fee > 0 else str(item_info['tkCommFee']))
			WXBOT.send_msg_by_uid(WXBOT.bot_conf[plugin_name]['message_send_with_fanli']%(sclick_data['data']['taoToken'],fanli_fee), msg['user']['id'])
	else:
		WXBOT.send_msg_by_uid(WXBOT.bot_conf[plugin_name]['message_search_fail'], msg['user']['id'])

def send_item_pic_to_uid(WXBOT,item_info,msg):
	pic_path = os.path.join(os.getcwd(),'temp',"item_"+str(item_info['auctionId'])+".jpg")
	file_object = open(pic_path, 'wb')
	file_object.write(requests.get(item_info['pictUrl']).content)
	file_object.close()
	WXBOT.send_img_msg_by_uid(pic_path,msg['user']['id'])
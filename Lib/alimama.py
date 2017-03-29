#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import cPickle
import json
from urllib import unquote
import top.api
import os
import re
import thread
import webbrowser


class alimama:
    """alimama功能类"""

    def __init__(self, siteid=None, zoneid=None, sign_account=None, login_type='local'):
        self.s = requests.Session()
        self.s.headers.update({
                                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'})
        self.account_info = ''  # 账号信息
        self.guideList = ''  # 导购信息，不包含网站推广、app推广等
        self.adzone = ''  # 所有的推广位信息
        self.selfadzon = ''  # 推广单元信息(包含媒体\推广位信息)
        self.siteid = siteid
        self.zoneid = zoneid

        # 必须参数，自动获取
        self.pvid = ''
        self._tb_token_ = ''

        # 获取方式参考文档2.2
        self.login_type = login_type  # qrcode,local,remote   支持二维码、本地、远程url调用登录
        self.sign_account = sign_account

        # 自己获取http://my.open.taobao.com/app/app_list.htm
        self.AppKey = '23391992'
        self.AppSecret = '25dd6135e70a9b711948509e2fc7dc1c'
        # 淘口令相关默认参数 (http://open.taobao.com/doc2/apiDetail.htm?apiId=26520&scopeId=11998)
        self.tkl_logo = ''
        self.tkl_user_id = '63060706'  # 淘宝客分享来源用户ID

        # 定向活动申请文案
        self.applyreason = u'几百个微信群+QQ群进行产品推广，麻烦通过！'

        # 文件缓存目录
        self.temp_pwd = os.path.join(os.getcwd(), 'temp')
        if os.path.exists(self.temp_pwd) == False:
            os.makedirs(self.temp_pwd)

        """
        尝试获取验证过的信息,并加载如果可用则不需要扫描二维码登录
        """
        try:
            self.s = cPickle.load(open(os.path.join(self.temp_pwd, "alimama.pkl"), "rb"))
            if self.check_login_status() == False:
                os.remove(os.path.join(os.getcwd(), self.temp_pwd, "alimama.pkl"))
                time.sleep(10)
                print '[INFO] 使用保存的alimama.pkl登录失败，重新调用auto_login登录!'
                self.auto_login()
            print '[INFO] Load alimama session success!'
        except Exception, e:
            self.auto_login()

    def create_tkl(self, text, url):
        """
        taobao域的url转淘口令
        接口文档http://open.taobao.com/doc2/apiDetail.htm?apiId=26520&scopeId=11998
        必须是淘宝链接才能转！！否则报错！
        """
        req = top.api.WirelessShareTpwdCreateRequest()
        req.set_app_info(top.appinfo(self.AppKey, self.AppSecret))

        data = {'text': text, 'url': url, 'user_id': self.tkl_user_id, 'logo': self.tkl_logo}
        req.tpwd_param = json.dumps(data)

        try:
            resp = req.getResponse()
            return True, resp
        except Exception, e:
            print '[ERROR] Create_tkl error:' + str(e)
            return False, str(e)

    def conver_tkl_2_url(self, tkl):
        """
        taobao域的淘口令转url
        """
        # 没找到接口~~~~~~~
        pass

    def get_queqiao_by_iid(self, iid):
        """
        通过iid获取鹊桥高佣金活动信息
        """
        url = u'http://zhushou.taokezhushou.com/api/v1/queqiaos/' + str(iid)
        try:
            data = self.s.get(url).json()
            return True, data
        except Exception, e:
            print '[ERROR] Get_queqiao_by_iid error:' + str(e)
            return False, e

    def get_campaigns_by_sid(self, sid):
        """
        根据店铺id查询店铺的定向推广活动
        """
        url = u'http://pub.alimama.com/shopdetail/campaigns.json?oriMemberId=' + str(sid)
        try:
            c = self.s.get(url).json()
            return True, c
        except Exception, e:
            print '[ERROR] Get_campaigns error:' + str(e)
            return False, e

    def apply_campaign(self, cid, kid):
        """
        申请定向推广通道
        cid：活动ID
        kid：keepid
        """
        url = u'http://pub.alimama.com/pubauc/applyForCommonCampaign.json'
        try:
            data = {
                'campId': cid,
                'keeperid': kid,
                'applyreason': self.applyreason,
                't': int(time.time()),
                'pvid': self.pvid,
                '_tb_token_': self._tb_token_
            }
            c = self.s.post(url, data=data).json()
            return c['info']['ok'], c
        except Exception, e:
            return False, e

    def apply_best_campaign(self, item_info):
        """
        申请商品的高佣金定向推广通道
        """
        result, data = self.get_campaigns_by_sid(item_info['sellerId'])
        if result:
            tkSpecialCampaignIdRateMap = item_info['tkSpecialCampaignIdRateMap']
            temp_rate = float(item_info['tkRate'])
            print u'[INFO] %s的默认佣金为-->%s' % (item_info['auctionId'], item_info['tkRate'])
            if tkSpecialCampaignIdRateMap != None:
                # print '[INFO] Find some tkSpecialCampaignIdRateMap ->%s'%(tkSpecialCampaignIdRateMap)
                try:
                    exsitApplyList = data['data']['exsitApplyList']
                except:
                    exsitApplyList = []
                campaignList = data['data']['campaignList']

                is_find = False
                temp_cid = ''
                # 比较获取最优的定向推广通道
                for x in tkSpecialCampaignIdRateMap:
                    # print x,tkSpecialCampaignIdRateMap[x]
                    if int(x) > 0:
                        if float(tkSpecialCampaignIdRateMap[x]) >= float(item_info['tkRate']) and float(
                                tkSpecialCampaignIdRateMap[x]) >= float(temp_rate):
                            temp_cid = x
                            temp_rate = tkSpecialCampaignIdRateMap[x]

                if temp_cid != '':
                    print u'[INFO] %s发现高佣金定向推广,活动ID：%s-->%s' % (item_info['auctionId'], str(temp_cid), temp_rate)

                    # 判断一下是否申请过这个高佣金通道
                    is_apply = False
                    for x in exsitApplyList:
                        if str(x['campaignId']) == str(temp_cid):
                            print u'[INFO] %s已经申请了高佣金活动了,活动ID：%s-->%s' % (
                            item_info['auctionId'], str(temp_cid), temp_rate)
                            is_apply = True
                            break
                    # h获取高佣金通道信息，并进行申请
                    if is_apply == False:
                        for x in campaignList:
                            if str(x['campaignId']) == str(temp_cid):
                                result, data = self.apply_campaign(x['campaignId'], x['shopKeeperId'])
                                if result:
                                    print u'[INFO] %s成功申请高佣金通道,原佣金%s,现佣金%s' % (
                                    item_info['auctionId'], str(item_info['tkRate']), temp_rate)
                                else:
                                    print u'[INFO] %s申请高佣金通道失败-->%s' % (item_info['auctionId'], data['info']['message'])
            print  u'[INFO] %s发现鹊桥高佣金推广，佣金比例%s' % (item_info['auctionId'], item_info['eventRate'])
            if item_info['eventRate'] != None:
                if float(item_info['eventRate']) > float(temp_rate):
                    print  u'[INFO] %s的鹊桥高佣金推广比例（%s）高于定向推广（%s）' % (
                    item_info['auctionId'], item_info['eventRate'], temp_rate)
                    return 1
            return 0

    def get_coupons_info(self, sid, cid, coupon_url=None):
        """
        获取代金券详情
        """
        if coupon_url == None:
            url = u"https://shop.m.taobao.com/shop/coupon.htm?&sellerId=%s&activityId=%s" % (sid, cid)
        else:
            url = coupon_url
        try:
            content = self.s.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'}).content.replace(
                '\t', '').replace('\n', '').replace(' ', '')
            content = re.findall(r'<divclass="coupon-info">(.*?)</div>', content)[0]
            result = re.findall(
                r'<dl><dt>(\d+?)元优惠券</dt><dd>剩<spanclass="rest">(\d+?)</span>张（已领用<spanclass="count">(\d+?)</span>张）</dd><dd>单笔满(\d+?)元可用，每人限领(\d+?)张</dd><dd>有效期:(.*?)至(.*?)</dd></dl>',
                content)
            return True, result[0]
        except Exception, e:
            print '[ERROR] Get_coupons_info by sid,cid error: %s-->%s' % (str(e), url)
            return False, e

    def get_coupons_base_by_sid_iid(self, sid, iid):
        """
        通过sid,iid获取店铺的代金券信息

        """
        url = u'http://zhushou3.taokezhushou.com/api/v1/coupons_base/' + str(sid) + '?item_id=' + str(iid)
        try:
            data = self.s.get(url).json()
            coupons_data = []
            for x in data['data']:
                result, c_data = self.get_coupons_info(sid, x['activity_id'])
                if result == True:
                    x['activity_info'] = c_data
                    x['sid'] = sid
                    coupons_data.append(x)
            return True, coupons_data
        except Exception, e:
            print '[Warn] Get_coupons_base by sid,iid warn:' + str(e)
            return False, e

    def match_best_coupon(self, item_info, coupons_info):
        """
        传入商品和代金券信息，自动计算出最合适的代金券
        """
        if len(coupons_info) == 0:
            return False, None
        find = False
        best_coupon = {'coupon': '', 'chae': 0}
        for x in coupons_info:
            print u'商品折扣价:%d，代金券满%d可减%d元' % (
            item_info['zkPrice'], int(x['activity_info'][3]), int(x['activity_info'][0]))
            if int(x['activity_info'][3]) <= item_info['zkPrice'] and int(x['activity_info'][0]) > best_coupon['chae']:
                best_coupon['coupon'] = x
                best_coupon['chae'] = int(x['activity_info'][0])
                find = True
        if find:
            print u'商品折扣价:%d，合适的代金券->满%d可减%d元' % (
            item_info['zkPrice'], int(x['activity_info'][3]), int(x['activity_info'][0]))
        return find, best_coupon

    def conver_sclickurl_to_iid(self, sclickurl):
        """
        转化淘宝客推广链接成淘宝商品id
        """
        try:
            r = self.s.get(sclickurl)
            url_1 = r.url
            url_2 = url_1[url_1.find('=') + 1:]
            url_2 = unquote(url_2)
            r = self.s.get(url_2, headers={'Referer': url_1})
            url_3 = r.url
            iid = int(url_3[url_3.find('id=') + 3:url_3.find('&')])
            return True, iid
        except Exception, e:
            print '[ERROR] Conver_sclickurl_to_iid error:' + str(e)
            return False, str(e)

    def get_sug_key(self, key):
        """
        根据用户提交的词，联想相关的词出来
        """
        try:
            url = u"https://suggest.taobao.com/sug?code=utf-8&q=%s" % (key)
            data = self.s.get(url).json()
            return True, data
        except Exception, e:
            print '[ERROR] Get_sug_key by key error:' + str(e)
            return False, e

    def get_guideList(self):
        """
        获取导购管理信息（推广管理->媒体管理->导购管理）
        """
        url = u'http://pub.alimama.com/common/site/generalize/guideList.json'
        try:
            c = self.s.get(url)
            self.guideList = c.json()
            return True, self.guideList
        except Exception, e:
            print '[ERROR] Get guideList error:' + str(e)
            return False, e

    def get_adzone(self):
        """
        获取推广位信息（推广管理->推广位管理）
        """
        url = u'http://pub.alimama.com/common/adzone/adzoneManage.json?tab=3'
        try:
            c = self.s.get(url)
            self.adzone = c.json()
            return True, self.adzone
        except Exception, e:
            print '[ERROR] Get adzone error:' + str(e)
            return False, e

    def get_selfadzone(self):
        """
        获取推广单元信息(包含媒体\推广位信息),这个是单品推广的时候获取推广单元信息使用的接口
        """
        url = u'http://pub.alimama.com/common/adzone/newSelfAdzone2.json?tag=29'
        try:
            c = self.s.get(url)
            self.selfadzon = c.json()
            return True, self.selfadzon
        except Exception, e:
            print '[ERROR] Get selfadzon error:' + str(e)
            return False, e

    # 下线！！！
    def create_auction_code(self, iid, siteid, adzoneid):
        """
        根据淘宝iid生成推广信息，不包含淘口令！！！！
        """
        url = u'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid=' + str(iid) + '&adzoneid' + str(
            adzoneid) + '&siteid=' + str(siteid)
        try:
            c = self.s.get(url).json()
            return True, c
        except Exception, e:
            print '[ERROR] Create_auction_code error:' + str(e)
            return False, e

    def create_auction_code_with_tkl(self, iid, siteid, adzoneid, item_info=None):
        """
        根据淘宝iid生成推广信息，包含淘口令！！！！包含淘口令！！！！包含淘口令！！！！同时自动匹配高佣金定向推广并申请！
        """
        result, qqhd_data = self.search_item_info_by_iid_use_queqiao(iid)
        if item_info != None:
            # result 0 默认申请即可, 1 鹊桥接口申请
            result = self.apply_best_campaign(item_info)
        if result == 0:
            url = u'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid=' + str(iid) + '&adzoneid=' + str(
                adzoneid) + '&siteid=' + str(siteid) + '&scenes=1&pvid=' + str(self.pvid) + '&t=' + str(
                int(time.time()))
        else:
            url = u'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid=' + str(iid) + '&adzoneid=' + str(
                adzoneid) + '&siteid=' + str(siteid) + '&scenes=3&channel=tk_qqhd&pvid=' + str(self.pvid) + '&t=' + str(
                int(time.time()))
        try:
            c = self.s.get(url).json()
            return True, c
        except Exception, e:
            print '[ERROR] Create_auction_code error:' + str(e)
            return False, e

    def search_item_info_by_iid(self, iid):
        """
        根据淘宝iid生成查询相关信息
        """
        url = u"http://pub.alimama.com/items/search.json?q=https://detail.tmall.com/item.htm?id=%s&_t=%s&auctionTag=&perPageSize=40" % (
        str(iid), str(int(time.time())))
        try:
            c = self.s.get(url).json()
            self.pvid = c['info']['pvid']
            return True, c
        except Exception, e:
            print '[ERROR] Create_auction_code error:' + str(e)
            return False, e

    def search_item_info_by_key(self, key):
        """
        根据关键词生成查询相关信息
        """
        url = u"http://pub.alimama.com/items/search.json?q=%s&_t=%s&auctionTag=&perPageSize=40" % (
        key, str(int(time.time())))
        try:
            c = self.s.get(url).json()
            self.pvid = c['info']['pvid']
            return True, c
        except Exception, e:
            print '[ERROR] Create_auction_code error:' + str(e)
            return False, e

    # 下线！！！
    def search_item_info_by_key_use_queqiao(self, key):
        """
        鹊桥接口——根据关键词生成查询相关信息
        """
        url = u"http://pub.alimama.com/items/channel/qqhd.json?q=%s&channel=qqhd&toPage=1&sortType=5&startBiz30day=10&perPageSize=50&shopTag=&t=%s" % (
        key, str(int(time.time())))

        try:
            c = self.s.get(url).json()
            self.pvid = c['info']['pvid']
            return True, c
        except Exception, e:
            print '[ERROR] Create_auction_code error:' + str(e)
            return False, e

            # 下线！！！

    def search_item_info_by_iid_use_queqiao(self, iid):
        """
        鹊桥接口——根据iid生成查询相关信息
        """
        url = u"http://pub.alimama.com/items/channel/qqhd.json?q=https://item.taobao.com/item.htm?id=" + str(
            iid) + "&channel=qqhd&toPage=1&sortType=1&startBiz30day=10&perPageSize=50&shopTag=&t=" + str(
            int(time.time()))
        try:
            c = self.s.get(url).json()
            self.pvid = c['info']['pvid']
            return True, c
        except Exception, e:
            print '[ERROR] Create_auction_code error:' + str(e)
            return False, e

    def get_youzhishangpin_xsl(self):
        """
        2016.10.12日，新增官方的导出优质商品成xls文件接口，保存文件到temp/yzsp.xls
        """
        url = "http://pub.alimama.com/coupon/qq/export.json?adzoneId=%s&siteId=%s" % (self.zoneid, self.siteid)
        try:
            c = self.s.get(url)
            file_object = open(os.path.join(self.temp_pwd, "yzsp.xls"), 'wb')
            file_object.write(self.s.get(url).content)
            file_object.close()
            return True, os.path.join(self.temp_pwd, "yzsp.xls")
        except Exception, e:
            print '[ERROR] Get_youzhishangpin_xsl error:' + str(e)
            return False, e

    def check_login_status(self):
        """
        检查登录状态
        """
        url = u'http://pub.alimama.com/common/getUnionPubContextInfo.json'
        try:
            c = self.s.get(url, allow_redirects=False).json()
            try:
                self.account_info = c
                self._tb_token_ = re.findall(r"<input name='_tb_token_' type='hidden' value='(.*?)'>",
                                             self.s.get('http://www.alimama.com/index.htm').content)[0]
                print u'[INFO] 登录参数检查memberid-->%s' % (c['data']['memberid'])
                print u'[INFO] 登录参数检查_tb_token_-->%s' % (self._tb_token_)
                print u'[INFO] Check login ok!'
                self.save_login_status()
                return True
            except Exception, e:
                os.remove(os.path.join(os.getcwd(), self.temp_pwd, "alimama.pkl"))
                print '[INFO] Check login false:', str(e)
                return False
        except Exception, e:
            print '[ERROR] Check login error:' + str(e)
            return False

    def save_login_status(self):
        """
        会话持久化存储，避免登录多次扫描二维码
        """
        cPickle.dump(self.s, open(os.path.join(self.temp_pwd, "alimama.pkl"), "wb"))
        print '[INFO] Save login session success!'

    def auto_login(self):
        """
        全自动登录函数，需配合task.exe使用！主要逻辑：如果判断登录状态失效则删除alimama.pkl，task.exe发现alimama.pkl被删除重新获取login.txt进行重新登录！
        或者调用http://g3.vivre.cn:8777/get_alimama_loginurl/获取！！！
        """
        try:
            if self.login_type == 'remote':
                url = self.s.get('http://g3.vivre.cn:8777/get_alimama_loginurl/').text
            else:
                if os.path.exists(os.path.join(os.getcwd(), self.temp_pwd, "alimama.pkl")):
                    os.remove(os.path.join(os.getcwd(), self.temp_pwd, "alimama.pkl"))
                time.sleep(5)
                url = open(os.path.join(os.getcwd(), self.temp_pwd, "url")).read()
            print  U'[INFO] 自动登录获取url-->%s' % (url)
            r = self.s.get(url)
            userid = re.findall(r'&userid=(.*?)&aplus', r.text)[0]
            print U'[INFO] 自动登录获取userid-->', userid
            if userid != '':
                # cPickle.dump(self.s, open(os.path.join(os.getcwd(),self.temp_pwd, "taobao.pkl"), "wb"))
                r = self.s.get(
                    'https://www.alimama.com/membersvc/my.htm?domain=taobao&service=user_on_taobao&sign_account=' + self.sign_account)
                self.s.get(r.url)
                self.check_login_status()
        except Exception, e:
            print u'[ERROR] 自动登录失败,错误信息：%s' % (e)

    def login(self, send_msg=None, target_id=None):
        while 1:
            # 按时间戳拼接二维码链接获取
            login_time = str(int(time.time())) + '_44'
            url = 'https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?from=alimama&_ksTS=' + login_time

            # 获取二维码链接和参数
            c = self.s.get(url).json()
            adToken = c['adToken']
            lgToken = c['lgToken']
            qr_img = "http:" + c['url']

            # 获取二维保存到本地
            print '[INFO] Please use TaobaoApp to scan the QR code .'

            file_object = open(os.path.join(self.temp_pwd, "alimamaqr.png"), 'wb')
            file_object.write(self.s.get(qr_img).content)
            file_object.close()

            webbrowser.open(os.path.join(os.getcwd(), 'temp', "alimamaqr.png"))

            # 为wx定制的，登录失败给指定人发消息
            if send_msg != None:
                send_msg.send_msg_by_uid(u'主人alimama失效啦,扫描二维码登录下呗！', target_id)
                send_msg.send_img_msg_by_uid(os.path.join(os.getcwd(), 'temp', "alimamaqr.png"), target_id)

                # 获取二维码扫描状态的url
            url = u"https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=" + str(
                lgToken) + "&defaulturl=http%3A%2F%2Fwww.alimama.com&_ksTS=" + login_time
            while 1:
                results = self.s.get(url).json()
                if results['code'] == '10004':
                    print '[INFO] Login code 10004->timeout.'
                    break
                if results['code'] == '10006':
                    print '[INFO] Login code 10006->success.'
                    self.s.get(results['url'])
                    break
                time.sleep(5)

            # print self.check_login_status()

            if self.check_login_status() == True:
                self.save_login_status()
                print '[INFO] QR code login ok!'
                return True


if __name__ == "__main__":

    # 通常就是：mm_43244382_15574862_59576937 -> mm_pid_siteid_adzoneid
    SITEID = '15574862'
    ADZONEID = '59576937'
    # 账号唯一标示，自动登陆alimama使用，参照文档2.2部分
    sign_account = 'ca387a0f250083076b1b2168c824881f'
    a = alimama(SITEID, ADZONEID, sign_account)

    """
    #获取tbk推广信息不包含淘口令
    result,data = a.create_auction_code('534321922732',siteid,adzoneid)
    #print data

    #获取tbk推广信息包含淘口令
    result,data = a.create_auction_code_with_tkl('534321922732',siteid,adzoneid)

    print json.dumps(data['data'],indent=4)

    result,data = a.search_item_info_by_iid('529444711644')
    #for x in  data['data']['pagelist'][0] :
        #print x,'-->',data['data']['pagelist'][0][x]

    result,data = a.search_item_info_by_key_use_queqiao('qq')

    #print json.dumps(data,indent=4)

    #生成淘口令
    result,data = a.create_tkl('XD分享群','https://www.taobao.com')
    print data['wireless_share_tpwd_create_response']['model']

    #淘宝客url转化成商品iid
    result,data = a.conver_sclickurl_to_iid('http://s.click.taobao.com/iqFjGVx')
    print data

    result,data = a.create_auction_code_with_tkl(data,siteid,adzoneid)

    print json.dumps(data['data'],indent=4)
    """

    siteid = '15574862'
    adzoneid = '59576937'

    result, iid = a.conver_sclickurl_to_iid('http://s.click.taobao.com/6OSPiUx')
    print iid
    result, data = a.search_item_info_by_iid(iid)
    if data['data']['pageList'] != None:
        item_info = data['data']['pageList'][0]
        print json.dumps(item_info, indent=4)
        result, data = a.create_auction_code_with_tkl(iid, siteid, adzoneid, item_info)
        print json.dumps(data['data'], indent=4)

    a.get_youzhishangpin_xsl()
    raw_input('')

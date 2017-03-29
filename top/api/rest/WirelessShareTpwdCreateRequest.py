'''
Created by auto_sdk on 2016.03.29
'''
from top.api.base import RestApi
class WirelessShareTpwdCreateRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.tpwd_param = None

	def getapiname(self):
		return 'taobao.wireless.share.tpwd.create'

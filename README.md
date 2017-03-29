#WxbotManage（当前内测中-V0.1）
基于Wxbot的微信多开管理和Webapi系统,可以实现如下内容：

1. 一个进程管理多个微信，互不影响，配置独立。
2. 可以通过Web界面对登录的微信进行管理。 
3. 提供webapi对登录的微信进行操控，可以接入任意语言开发的系统。
4. 消息处理插件化，可以自定义插件编写实现多种功能。例如：转发消息给其他系统处理，群监控，自动回复，群管理等。

感谢liuwons的Wxbot代码：https://github.com/liuwons/wxBot

收费提问咨询解决问题

![](http://bbs.vivre.cn/uploads/image/201612/14805865236273.jpg)


## 1 快速开始
### 1.1 安装依赖库
此版本只能运行于Python 2环境，python版本为2.7 下载地址：https://www.python.org/downloads/release/python-2712/

使用如下命令安装所依赖的库:
```bash
pip install -r requirements.txt
```
如果报错请按照错误信息升级pip程序版本。

当然，如果你是Coding的用户，可以直接去Fork本代码，然后使用WebIDE功能快速搭建运行环境！WebIDE地址：https://ide.coding.net/dashboard

WebIDE使用：

1. 创建工作空间，可以使用Git地址https://git.coding.net/vivre/WxbotManage.git 直接创建
2. 使用pip安装所需库文件
3. 运行python main.py
4. 点击右侧访问连接，生成临时访问地址即可访问，账号密码 admin  admin

### 1.2 程序
直接用 `python` 运行代码 ***main.py*** :

``` python
python main.py
```
即可调用webapi提供的相关接口

然后访问http://127.0.0.1:8080  帐号密码均为admin 即可对微信进行管理。

![](http://bbs.vivre.cn/uploads/image/201611/14792600062342.png)

### 1.3 插件
插件可以实现自定义处理微信消息的功能,插件存放在`plugin`目录,并且在`handle_msg_all`函数中自动动态调用

#### 1.3.1 插件hello word !

```python
#!/usr/bin/env python
# coding: utf-8
import requests

#必须是run函数，自动调用！
def run(WXBOT,msg,plugin_name):
	try:
	    #插件配置载入，不存在就给一个默认配置文件
		WXBOT.bot_conf[plugin_name]
	except:
	    #加载默认配置文件
		WXBOT.bot_conf[plugin_name] = ''

	try:
	    #do something  命中消息啊做些啥啊
		print plugin_name
	except Exception,e:
		print u'[ERRO]%s插件运行错误--->%s'%(plugin_name,e)
```

| 字段名 | 字段内容 |
| ----- | --- |
| `WXBOT` | 登录的账号对象，可以调用wxbot内部的任意对象，参照**3 wxbot主要对象和函数** |
| `msg` | json 格式的微信消息，参考 **2 wxbot消息msg数据结构详解** |
| `plugin_name` |  str 格式的插件名称和插件文件名相同 |

系统自带了3个插件

msg_forward.py              通过http协议post给其他系统的url进行处理！格式请查看msg_foward里面的data字典！**这样可以实现任意语言的微信机器人插件！！**

groupmanage.py              监控微信群成员进群、踢出群、群红包、群名称修改等消息并进行处理！

zhaqunjiankong.py           监控微信群的文字消息匹配消息中的敏感词数量来自动踢出某些群内的捣乱分子！

auto_apply_user_add.py      自动通过好友请求，并进行相应处理！


插件设计建议：

如果是多账号管理，建议和自己得系统对接，将数据都保存到自己得数据中，方便进行管理！！

插件中使用数据库请参考： http://webpy.org/cookbook/multidbs.zh-cn

### 1.4 webapi
系统启动后会自动开启http服务并提供微信机器人的相关接口调用服务，地址 **http://服务器IP:8080**

**http://服务器IP:8080/static/webapi.html**

webapi在线调试：http://apizza.cc/console/project/c98fde44f3e16e8952db37e4a54a1216/pass   密码：wxhlw


### 1.5 目录结构详解
```shell
├─data/   安装文件、web数据库
├─docs/   文档
├─Lib/    公共类库目录
├─plugin/ 微信插件目录
├─static/ web静态目录，存放微信相关的临时文件
├─temp/   系统临时目录
├─top/    淘宝的sdk
├─webapi/ webapi目录
├─webui_templates/ webui的html代码目录
└─main.py 主进程
```


## 2 wxbot消息msg数据结构详解
此处msg消息在handle_msg_all函数中进行处理，为核心消息体！！！可按照wxbot解析后得消息结构对所有得微信小心进行响应核处理！

`handle_msg_all` 函数的参数 `msg` 是代表一条消息的字典。字段的内容为：

| 字段名 | 字段内容 |
| ----- | --- |
| `msg_type_id` | 整数，消息类型，具体解释可以查看 **消息类型表** |
| `msg_id` | 字符串，消息id |
| `content` | 字典，消息内容，具体含有的字段请参考 **消息类型表** ，一般含有 `type`(数据类型)与 `data`(数据内容)字段，`type` 与 `data`的对应关系可以参考 **数据类型表**  |
| `user` | 字典，消息来源，字典包含 `name`(发送者名称,如果是群则为群名称，如果为微信号，有备注则为备注名，否则为微信号或者群昵称)字段与 `id`(发送者id)字段，都是字符串  |

### 2.1 消息类型表

| 类型号 | 消息类型 | `content` |
| ----- | --- | ------ |
| 0 | 初始化消息，内部数据 | 无意义，可以忽略 |
| 1 | 自己发送的消息 | 无意义，可以忽略 |
| 2 | 文件消息 | 字典，包含 `type` 与 `data` 字段 |
| 3 | 群消息 | 字典， 包含 `user` (字典，包含 `id` 与 `name`字段，都是字符串，表示发送此消息的群用户)与 `type` 、 `data` 字段，红包消息只有 `type` 字段， 文本消息还有detail、desc字段， 参考 **群文本消息** |
| 4 | 联系人消息 | 字典，包含 `type` 与 `data` 字段 |
| 5 | 公众号消息 | 字典，包含 `type` 与 `data` 字段 |
| 6 | 特殊账号消息 | 字典，包含 `type` 与 `data` 字段 |
| 99 | 未知账号消息 | 无意义，可以忽略 |

### 2.2 数据类型表

| `type` | 数据类型 | `data` |
| ---- | ---- | ------ |
| 0 | 文本 | 字符串，表示文本消息的具体内容 |
| 1 | 地理位置 | 字符串，表示地理位置 |
| 3 | 图片 | 字符串，图片数据的url，HTTP POST请求此url可以得到jpg文件格式的数据 |
| 4 | 语音 | 字符串，语音数据的url，HTTP POST请求此url可以得到mp3文件格式的数据 |
| 5 | 名片 | 字典，包含 `nickname` (昵称)， `alias` (别名)，`province` (省份)，`city` (城市)， `gender` (性别)字段 |
| 6 | 动画 | 字符串， 动画url, HTTP POST请求此url可以得到gif文件格式的数据 |
| 7 | 分享 | 字典，包含 `type` (类型)，`title` (标题)，`desc` (描述)，`url` (链接)，`from` (源网站)字段 |
| 8 | 视频 | 不可用 |
| 9 | 视频电话 | 不可用 |
| 10 | 撤回消息 | 不可用 |
| 11 | 空内容 | 空字符串 |
| 12 | 红包 | 不可用 |
| 99 | 未知类型 | 不可用 |

### 2.3 群文本消息

由于群文本消息中可能含有@信息，因此群文本消息的 `content` 字典除了含有 `type` 与 `data` 字段外，还含有 `detail` 与 `desc` 字段。

各字段内容为：

| 字段 | 内容 |
| --- | ---- |
| `type` | 数据类型， 为0(文本) |
| `data` | 字符串，消息内容，含有@信息 |
| `desc` | 字符串，删除了所有@信息 |
| `detail` | 数组，元素类型为含有 `type` 与 `value` 字段的字典， `type` 为字符串 ***str*** (表示元素为普通字符串，此时value为消息内容) 或 ***at*** (表示元素为@信息， 此时value为所@的用户名) |

### 2.4群消息示例
#### 2.4.1 群文本消息  msg_type_id=3,content.type=0
```json
{
    'content': {
        'data': u'a',
        'desc': u'a',
        'type': 0,
        'user': {
            'id': u'@4978f7389c52957e7f8be546bf88e250a3fbf5f68daf22036eab7ce4e190730a',
            'name': u'A0\u6dd8\u5b9d\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0'
        },
        'detail': [
            {
                'type': 'str',
                'value': u'a'
            }
        ]
    },
    'msg_id': u'7786992096423040253',
    'msg_type_id': 3,
    'to_user_id': u'@431b6e101bc69aaa942c37ae3ad5f9da',
    'user': {
        'id': u'@@31e5c822939f450eafc40f49ae72108bd3f7db54243b00c3067cff9ddaef5590',
        'name': u'unknown'
    }
}
```

#### 2.4.2 群图片消息 msg_type_id=3,content.type=3
```json
{
    'content': {
        'data': u'https: //wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetmsgimg?MsgID=8254739790581730562&skey=@crypt_6097b1dd_ad1aa702a9bf1f61d4595a90a6c51836',
        'type': 3,
        'user': {
            'id': u'@4978f7389c52957e7f8be546bf88e250a3fbf5f68daf22036eab7ce4e190730a',
            'name': u'A0\u6dd8\u5b9d\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0'
        },
        'img': '二进制图片内容'
    },
    'msg_id': u'8254739790581730562',  #会以img_8254739790581730562.jpg保存到temp目录下
    'msg_type_id': 3,
    'to_user_id': u'@431b6e101bc69aaa942c37ae3ad5f9da',
    'user': {
        'id': u'@@31e5c822939f450eafc40f49ae72108bd3f7db54243b00c3067cff9ddaef5590',
        'name': u'unknown'
    }
}
```

#### 2.4.3 群内@消息 msg_type_id=3,content.type=0 和文本消息一样，但是content.detail中第一个type为at
```json
{
    'content': {
        'data': u'@\u5c0fVk',
        'desc': u'k',
        'type': 0,
        'user': {
            'id': u'@4978f7389c52957e7f8be546bf88e250a3fbf5f68daf22036eab7ce4e190730a',
            'name': u'A0\u6dd8\u5b9d\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0'
        },
        'detail': [
            {
                'type': 'at',
                'value': u'\u5c0fV'
            },
            {
                'type': 'str',
                'value': u'k'
            }
        ]
    },
    'msg_id': u'2672398598809507413',
    'msg_type_id': 3,
    'to_user_id': u'@431b6e101bc69aaa942c37ae3ad5f9da',
    'user': {
        'id': u'@@31e5c822939f450eafc40f49ae72108bd3f7db54243b00c3067cff9ddaef5590',
        'name': u'unknown'
    }
}
```

#### 2.4.4 群管控消息 msg_type_id=3,content.type=12
```json
{
    'content': {
        'data': u'"A0\u6dd8\u5b9d\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0"\u9080\u8bf7"A\u6162\u6b65\u4e91\u7aef"\u52a0\u5165\u4e86\u7fa4\u804a',
        'type': 12,
        'user': {
            'id': u'"A0\u6dd8\u5b9d
\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0"\u9080\u8bf7"A\u6162\u6b65\u4e91\u7aef"\u52a0\u5165\u4e86',
            'name': 'unknown'
        }
    },
    'msg_id': u'8260279518753575553',
    'msg_type_id': 3,
    'to_user_id': u'@431b6e101bc69aaa942c37ae3ad5f9da',
    'user': {
        'id': u'@@31e5c822939f450eafc40f49ae72108bd3f7db54243b00c3067cff9ddaef5590',
        'name': u'unknown'
    }
}
```


### 2.5 私聊消息示例
#### 2.5.1 私聊文本消息 msg_type_id=4,content.type=0
```json
{
    'content': {
        'data': u'a',
        'type': 0
    },
    'msg_id': u'3199219329947948605',
    'msg_type_id': 4,
    'to_user_id': u'@431b6e101bc69aaa942c37ae3ad5f9da',
    'user': {
        'id': u'@4978f7389c52957e7f8be546bf88e250a3fbf5f68daf22036eab7ce4e190730a',
        'name': u'A0\u6dd8\u5b9d\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0'
    }
}
```

#### 2.5.2 私聊图片消息 msg_type_id=4,content.type=3
```json
{
    'content': {
        'data': u'https: //wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetmsgimg?MsgID=7473116563528914761&skey=@crypt_6097b1dd_ad1aa702a9bf1f61d4595a90a6c51836',
        'type': 3,
        'img': ''
    },
    'msg_id': u'7473116563528914761',
    'msg_type_id': 4,
    'to_user_id': u'@431b6e101bc69aaa942c37ae3ad5f9da',
    'user': {
        'id': u'@4978f7389c52957e7f8be546bf88e250a3fbf5f68daf22036eab7ce4e190730a',
        'name': u'A0\u6dd8\u5b9d\u4f18\u60e0\u52a9\u624b-\u60a0\u60a0'
    }
}
```


### 3 wxbot主要对象和函数
### 3.1 主要对象--存放微信联系人列表得地方

登录并初始化之后,含有以下的可用数据:

| 属性 | 描述 |
| ---- | ---- |
| `contact_list` | 当前用户的微信联系人列表 |
| `group_list` | 当前用户的微信群列表 |
| `public_list` | 当前用户关注的公众号列表 |
| `special_list` | 特殊账号列表 |
| `session` | **WXBot** 与WEB微信服务器端交互所用的 **Requests** `Session` 对象 |

#### 3.1 主要函数列表

| 方法 | 描述 |
| ---- | --- |
| `get_icon(uid, gid)` | 获取联系人或者群聊成员头像并保存到本地文件 ***img_[uid].jpg***  , `uid` 为用户id, `gid` 为群id |
| `get_head_img(id)` | 获取用户头像并保存到本地文件 ***img_[id].jpg*** ，`id` 为用户id(Web微信数据) |
| `get_msg_img(msgid)` | 获取图像消息并保存到本地文件 ***img_[msgid].jpg*** , `msgid` 为消息id(Web微信数据) |
| `get_voice(msgid)` | 获取语音消息并保存到本地文件 ***voice_[msgid].mp3*** , `msgid` 为消息id(Web微信数据) |
| `get_contact()` | 全面更新`3.1`中存储得所有联系人信息，通常在通讯录变更得时候使用，不能频繁调用！会导致账号无法获取任何联系人信息！ |
| `get_contact_name(uid)` | 获取微信id对应的名称，返回一个可能包含 `remark_name` (备注名), `nickname` (昵称), `display_name` (群名称)的字典|
| `send_msg_by_uid(word, dst)` | 向好友发送消息，`word` 为消息字符串，`dst` 为好友用户id(Web微信数据) |
| `send_img_msg_by_uid(fpath, dst)` | 向好友发送图片消息，`fpath` 为本地图片文件路径，`dst` 为好友用户id(Web微信数据) |
| `send_file_msg_by_uid(fpath, dst)` | 向好友发送文件消息，`fpath` 为本地文件路径，`dst` 为好友用户id(Web微信数据) |
| `send_msg_by_uid(word, dst)` | 向好友发送消息，`word` 为消息字符串，`dst` 为好友用户id(Web微信数据) |
| `send_msg(name, word, isfile)` | 向好友发送消息，`name` 为好友的备注名或者好友微信号， `isfile`为 `False` 时 `word` 为消息，`isfile` 为 `True` 时 `word` 为文件路径(此时向好友发送文件里的每一行)，此方法在有重名好友时会有问题，因此更推荐使用 `send_msg_by_uid(word, dst)` |
| `is_contact(uid)` | 判断id为 `uid` 的账号是否是本帐号的好友，返回 `True` (是)或 `False` (不是) |
| `is_public(uid)` | 判断id为 `uid` 的账号是否是本帐号所关注的公众号，返回 `True` (是)或 `False` (不是) |
| `apply_useradd_requests(RecommendInfo)` | 处理`RecommendInfo`结构体，自动响应好友添加请求 |
| `add_groupuser_to_friend_by_uid(uid,VerifyContent)` | 主动像群友发送好友添加请求，`VerifyContent`为好友申请内容 |
| `add_friend_to_group(uid,group_name)` | 邀请好友`uid`进如指定得群`group_name` |
| `delete_user_from_group(uname,gid)` | 从指定得群id`gid`中通过群成成员名称删除群成员`uname` |
| `set_group_name(gid,gname)` | 设置指定群id得群名称 |

详细使用请参考我提供的部分插件代码！！

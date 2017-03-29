# Wxbot

## 函数

### get_icon(uid, gid)

#### 获取联系人或者群聊成员头像并保存到本地文件 img_[uid].jpg , uid 为用户id, gid 为群id

### get_head_img(id)

#### 获取用户头像并保存到本地文件 img_[id].jpg ，id 为用户id(Web微信数据)

### get_msg_img(msgid)

#### 获取图像消息并保存到本地文件 img_[msgid].jpg , msgid 为消息id(Web微信数据)

### get_voice(msgid)

#### 获取语音消息并保存到本地文件 voice_[msgid].mp3 , msgid 为消息id(Web微信数据)

### get_contact()

#### 全面更新3.1中存储得所有联系人信息，通常在通讯录变更得时候使用，不能频繁调用！会导致账号无法获取任何联系人信息！

### get_contact_name(uid)

#### 获取微信id对应的名称，返回一个可能包含 remark_name (备注名), nickname (昵称), display_name (群名称)的字典

### send_msg_by_uid(word, dst)

#### 向好友发送消息，word 为消息字符串，dst 为好友用户id(Web微信数据)

### send_img_msg_by_uid(fpath, dst)

#### 向好友发送图片消息，fpath 为本地图片文件路径，dst 为好友用户id(Web微信数据)

### send_file_msg_by_uid(fpath, dst)

#### 向好友发送文件消息，fpath 为本地文件路径，dst 为好友用户id(Web微信数据)

### send_msg_by_uid(word, dst)

#### 向好友发送消息，word 为消息字符串，dst 为好友用户id(Web微信数据)

### send_msg(name, word, isfile)

#### 向好友发送消息，name 为好友的备注名或者好友微信号， isfile为 False 时 word 为消息，isfile 为 True 时 word 为文件路径(此时向好友发送文件里的每一行)，此方法在有重名好友时会有问题，因此更推荐使用 send_msg_by_uid(word, dst)

### is_contact(uid)

#### 判断id为 uid 的账号是否是本帐号的好友，返回 True (是)或 False (不是)

### is_public(uid)

#### 判断id为 uid 的账号是否是本帐号所关注的公众号，返回 True (是)或 False (不是)

### apply_useradd_requests(RecommendInfo)

#### 处理RecommendInfo结构体，自动响应好友添加请求

### add_groupuser_to_friend_by_uid(uid,VerifyContent)

#### 主动像群友发送好友添加请求，VerifyContent为好友申请内容

### add_friend_to_group(uid,group_name)

#### 邀请好友uid进如指定得群group_name

### delete_user_from_group(uname,gid)

#### 从指定得群idgid中通过群成成员名称删除群成员uname

### set_group_name(gid,gname)

#### 设置指定群id得群名称

## 数据

### contact_list 

#### 当前用户的微信联系人列表

### group_list

#### 当前用户的微信群列表

### public_list

#### 当前用户关注的公众号列表

### special_list

#### 特殊账号列表

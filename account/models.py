# -*- coding:utf-8 -*-
# django library
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from django.contrib.sessions.models import Session

#our own code
from role.models import Role
from authority.models import Permission

class UserProfile(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'user_profile'
    # 用户对象，使用django 默认User对象
    user = models.OneToOneField(User)
    # 部门
    department = models.CharField(max_length=128, blank=True)
    # 电话
    phone = models.CharField(max_length=15, blank=True)
    # 真实姓名
    realname = models.CharField(max_length=32)

# 仅用于页面显示
class UserExtend():
    def __init__(self):
        # 序号
        self.id = None
        # 用户名
        self.username = None
        # 电子邮件
        self.email = None
        # 角色
        self.roles = None
        # 角色ID 列表
        self.role_ids = None
        # 部门 
        self.department = None
        # 联系方式
        self.phone = None
        # 真实姓名
        self.realname = None


def user2Extend(users):
    user_list = []
    for item in users:
        user_list.append(getUser(item.id))
    return user_list

# 获取用户
def getUser(user_id):
    auth_user = User.objects.get(id=user_id)
    if not auth_user:
        return None
    user = UserExtend()
    user.id = auth_user.id
    user.username = auth_user.username
    user.email = auth_user.email
    user.department = auth_user.userprofile.department 
    user.phone = auth_user.userprofile.phone
    user.realname = auth_user.userprofile.realname
    
    role_str = ""
    role_id_list = []
    role_list = auth_user.role_set.all()
    for i in range(len(role_list)):
        if i > 0:
            role_str +=","
        role_str +=role_list[i].name
        role_id_list.append(role_list[i].id)
    user.roles = role_str
    user.role_ids = role_id_list
    return user
    

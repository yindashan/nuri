# -*- coding:utf-8 -*-
# django library
from django.db import models
from django.contrib.auth.models import User

# our own code
from authority.models import Permission

# 角色　角色只是相当于权限的一个集合,能够方便快捷的为用户分配权限   参看　auth_group
class Role(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'role'
    #主键由Django生成
    name = models.CharField(max_length=64) # 角色名称  
    desc = models.CharField(max_length=255) # 角色描述
    
    # 权限
    permissions = models.ManyToManyField(Permission) # 角色和权限多对多关联
    # 用户
    users = models.ManyToManyField(User) # 用户与角色多对多关联
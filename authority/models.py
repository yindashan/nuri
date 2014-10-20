# -*- coding:utf-8 -*-
# django library
from django.db import models
from django.contrib.auth.models import User

# 权限 每一个权限控制点在此表中表现为一条记录 参看auth_permission
class Permission(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'permission'
    #主键由Django生成
    codename = models.CharField(max_length=64,unique = True) # codename 用于控制  
    desc = models.CharField(max_length=255) # 描述
    #类型 1:用户和角色 2:应用项　相关权限 3:监控项　相关权限 4:树状节点 相关权限
    type = models.IntegerField()
    
    # 用户
    users = models.ManyToManyField(User) # 用户与权限多对多关联
    

    

        
# -*- coding:utf-8 -*-
import time
import json
from django.db import models
from django.conf import settings
from redis import RedisError
from appitem.models import AppService
from celery import task

# URL信息
class URLInfo(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'urlinfo'
    # url信息
    url = models.CharField(max_length=1000)
    # 预定响应时间(单位为秒)
    responsetime = models.CharField(max_length=16)
    # url返回内容类型,现在支持三种类型：xml/json/text
    type = models.CharField(max_length=64)
    # 用于匹配内容的target
    target = models.CharField(max_length=64)
    # 用于匹配内容的value
    value = models.CharField(max_length=64)
    # 用于标识该项是否删除，is_deleted:0表示已删除，１表示未删除
    is_deleted = models.IntegerField(default=1)
    
    #外键  应用服务
    app = models.ForeignKey(AppService) # 多对一关联




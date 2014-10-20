# -*- coding:utf-8 -*-
import time
import json
from django.db import models
from django.conf import settings
from redis import RedisError
from appitem.models import AppService
from celery import task

# TCP信息
class TCPInfo(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'tcpinfo'
    # port信息
    port = models.CharField(max_length=16)
    # 预定响应时间(单位为秒)
    responsetime = models.CharField(max_length=16)
    
    #外键  应用服务
    app = models.ForeignKey(AppService) # 多对一关联




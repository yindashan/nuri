# -*- coding:utf-8 -*-
from django.db import models

# 机房与IP对应信息
class NOCIP(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'nocip'
    # 机房编号
    nocid = models.CharField(max_length=64)
    # IP
    ip = models.CharField(max_length=64)


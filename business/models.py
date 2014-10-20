# -*- coding:utf-8 -*-
from django.db import models
from appitem.models import AppService, AppRepr

# 业务线
class BusinessLine(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'business_line'
    # 业务名称
    name = models.CharField(max_length=64)
    # 备注
    comment = models.CharField(max_length=256)
    # 运维接口人
    op_interface = models.CharField(max_length=32)
    # 运维接口人电话
    op_phone = models.CharField(max_length=20)
    # 业务方接口人
    bn_interface = models.CharField(max_length=32)
    # 业务方接口人电话
    bn_phone = models.CharField(max_length=20)
    
    # 注:业务线跟应用项实际应该是一对多的关系
    apps = models.ManyToManyField(AppService) 
    
# 用于页面展现的类   
class BnLineRepr(object):
    def __init__(self, other):
        self.id = other.id
        self.name = other.name
        self.comment = other.comment
        self.op_interface= other.op_interface
        self.op_phone = other.op_phone
        self.bn_interface = other.bn_interface
        self.bn_phone = other.bn_phone
        
        self.app_list = []
        # 应用信息
        for app in other.apps.all():
            self.app_list.append(AppRepr(app))
            
        
        
    

  
    
    
    
    
    
    
    
    
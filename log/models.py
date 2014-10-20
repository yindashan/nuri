# -*- coding:utf-8 -*-
from django.db import models
from utils.constants import log_level_dict
from utils.constants import log_type_dict
import datetime
class Log(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'log'
    
    create_time = models.DateTimeField(u"创建时间", default=datetime.datetime.now) # 创建时间，格式为'0000-00-00 00:00:00'
    username = models.CharField(max_length=64) # 操作用户名称
    content = models.CharField(max_length=255) # 操作内容
    log_type = models.IntegerField(default=0) # 日志类型 1:用户和角色,2:应用项,3:监控项,4:节点  目前只针对前三项记录日志
    relate_id = models.IntegerField(null=True) # 关联主键id
    level = models.IntegerField(default=1) # 日志级别。“0”为DEBUG，“1”为INFO，“2”为WARN，“3”为ERROR
    
    def __unicode__(self):
        return self.username
        
class LogExtend():
    def __init__(self):
        self.id = None
        self.create_time = None
        self.usename = None
        self.content = None
        self.log_type = None
        self.relate_id = None
        self.level = None
        
        
def log2Extend(logs):
    item_list = []
    for log in logs:
        item = LogExtend()
        item.id = log.id
        item.create_time = log.create_time.strftime("%Y-%m-%d %H:%M:%S", )
        item.username = log.username
        item.content = log.content
        item.log_type = log_type_dict[log.log_type]
        item.relate_id = log.relate_id
        item.level = log_level_dict[log.level]
        item_list.append(item)
    return item_list
    
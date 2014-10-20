# -*- coding:utf-8 -*-
# 检查主机是否存活，对不同的主机采用不同的检查策略
import json
import time
import logging
from django.db import models
from celery import task
from hostalive.rules import RuleFactory
from django.conf import settings
from datetime import datetime
from notify.models import notify_host


# 对一组机器，进行存活检查的设定
# 主机只有 up / down　两种状态
class AliveCheck(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'alive_check'
    
    # IP列表    
    ip_list = models.TextField()
    
    # IP对应的主机ID列表,以逗号分隔  
    host_list = models.TextField()
    
    # 名称
    name = models.CharField(max_length=64)
    
    # 备注
    comment = models.CharField(max_length=128)
    
    # 重试次数
    retry_count = models.IntegerField(default=2)
    
    # 通知间隔　单位: 分钟
    # 注: 上次通知和当前之间的差值如果小于此值, 就不触发报警
    notify_interval = models.IntegerField(default=60)
    
    # 邮件列表
    email_list = models.CharField(max_length = 255)
    
    # 手机列表
    mobile_list = models.CharField(max_length = 255)
    
# 扩展类，用于在index页展示    
class AliveCheckRepr(object):
    def __init__(self, other):
        self.id = other.id
        self.name = other.name
        self.comment = other.comment
        self.retry_count = other.retry_count
        self.host_count = len(other.host_list.split(','))
    
# 通过这些规则来判断主机是否存活   
class AliveRule(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'alive_rule'
    
    # 名称    
    name = models.CharField(max_length=64)
    # 标示符
    # 一般为类名
    sign = models.CharField(max_length=64)
    
    # 主机存活检查规则
    achecks = models.ManyToManyField(AliveCheck) 
    
# 周期性的判断主机是否存活
@task
def check_host_alive():
    logger = logging.getLogger('django')
    start_time = time.time()
    
    pipe = settings.REDIS_DB.pipeline()
    criterion_list = AliveCheck.objects.all()
    for criterion in criterion_list:
        logger.info(u'使用检查标准:%s,检查主机%s, 对应IP列表:%s,是否存活', criterion.name, 
            criterion.host_list, criterion.ip_list)
        host_list = criterion.host_list.split(',')
        for host in host_list:
            # 获取主机上一次的状态
            key = 'host_alive_' + host
            
            if not settings.REDIS_DB.exists(key):
                pipe.hset(key, 'current_status', 'UP')
                pipe.hset(key, 'current_attempt', 0)
                pipe.hset(key, 'last_state_change', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                pipe.hset(key, 'last_notification', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                pipe.execute()
            
            status_dict = settings.REDIS_DB.hgetall(key)
            current_status = status_dict.pop('current_status', 'UP')
            current_attempt = status_dict.pop('current_attempt', 0)
            current_attempt = int(current_attempt)
            last_notification = status_dict.pop('last_notification', '2014-01-01 00:00:00')
            last_notification = datetime.strptime(last_notification, '%Y-%m-%d %H:%M:%S')
            
            rule_list = criterion.aliverule_set.all()
            
            status = 'DOWN'
            for rule in rule_list:
                obj = RuleFactory.genRule(rule.sign)
                if obj.check(host):
                    status = 'UP'
                    logger.info(u'检查主机:%s,使用规则:%s,得到状态:%s', host, rule.sign, status)
                    break
                else:
                    logger.info(u'检查主机:%s,使用规则:%s,得到状态:%s', host, rule.sign, 'DOWN')
                    
            logger.info(u'【结论】检查主机:%s,得到状态:%s', host, status)
                
            if current_status != status or status == 'DOWN':
                current_attempt = current_attempt + 1
                pipe.hset(key, 'current_attempt', current_attempt)
            
                if current_attempt >= criterion.retry_count:
                    
                    # 1. 重新设置主机的存活情况
                    pipe.hset(key, 'current_status', status)
                    pipe.hset(key, 'current_attempt', 0)
                    
                    if current_status != status:
                        pipe.hset(key, 'last_state_change', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    
                    # 2. 产生通知信息 以及　触发短信和邮件报警
                    # recovery 事件不受notify_interval影响
                    if status == 'UP':
                        notify_host.delay(criterion, host, status, datetime.now())
                    else:
                        margin = total_seconds(datetime.now() - last_notification)
                        if margin > criterion.notify_interval * 60:
                            pipe.hset(key, 'last_notification', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            notify_host.delay(criterion, host, status, datetime.now())
            else:
                pipe.hset(key, 'current_attempt', 0)
                
    pipe.execute()
    end_time = time.time()
    logger.info(u'进行主机存活性检查，耗时:%d 秒', end_time - start_time)
    
# timedelta　对象转换成 秒    
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    
    
            
                
                    
            
        
    

    
    
    
    
    
    
        
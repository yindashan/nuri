# -*- coding:utf-8 -*-

import json
import random, time
from django.db import models
from celery import task
from redis import RedisError
from django.conf import settings

# 应用通知
class Notification(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'notification'
    # 发生时间
    time = models.DateTimeField()
    # host 主机
    host = models.CharField(max_length=32)
    # 应用
    appname = models.CharField(max_length=32)
    # 通知类型
    type = models.CharField(max_length=20)
    # 应用当前状态
    state = models.CharField(max_length=20)
    # 信息
    information = models.TextField()
    
# 主机通知
class HostEvent(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'host_event'
    # 发生时间
    time = models.DateTimeField()
    # host 主机
    host = models.CharField(max_length=32)
    # 通知类型  PROBLEM / RECOVERY
    type = models.CharField(max_length=20)
    # 应用当前状态  UP / DOWN
    state = models.CharField(max_length=20)
    # 信息
    information = models.TextField()
    
# 从redis队列中取出多条数据　
def pop_multi(pipeline, key, count):
    for i in range(count):
        pipeline.lpop(key)
        
    item_list = pipeline.execute()
    result_list = []
    for item in item_list:
        if item:
            result_list.append(item)
            
    return result_list
    
# 应用通知回写
@task
def notification_writeback():
    pipe = settings.REDIS_DB.pipeline()
    count = 0
    while True:
        item_list = []
        try:
            item_list = pop_multi(pipe, 'notification', 200)
        except RedisError, e:
            # FIXME
            pass
                
        res_list = []
        for item in item_list:
            dd = json.loads(item)
            nt = Notification()
            nt.time = dd['time']
            nt.host = dd['host']
            nt.appname = dd['appname']
            nt.type = dd['type']
            nt.state = dd['state']
            nt.information = dd['information']
            
            res_list.append(nt)
        
        if res_list:
            # 对数据库进行回写
            Notification.objects.bulk_create(res_list)
            
            # 队列中的记录还没有被全部回写，休眠一段时间，重复上面过程
            # 50ms ~ 200ms
            sleep_time = random.randint(50, 200)
            time.sleep(float(sleep_time) / 1000)
            
        count += len(res_list)
        if len(res_list) <= 0 or count >= settings.TASK_MAX_WRITEBACK:
            break

# 主机通知回写
@task
def host_event_writeback():
    pipe = settings.REDIS_DB.pipeline()
    count = 0
    while True:
        item_list = []
        try:
            item_list = pop_multi(pipe, 'host_event', 200)
        except RedisError, e:
            # FIXME
            pass
                
        res_list = []
        for item in item_list:
            dd = json.loads(item)
            nt = HostEvent()
            nt.time = dd['time']
            nt.host = dd['host']
            nt.type = dd['type']
            nt.state = dd['state']
            nt.information = dd['information']
            
            res_list.append(nt)
        
        if res_list:
            # 对数据库进行回写
            HostEvent.objects.bulk_create(res_list)
            
            # 队列中的记录还没有被全部回写，休眠一段时间，重复上面过程
            # 50ms ~ 200ms
            sleep_time = random.randint(50, 200)
            time.sleep(float(sleep_time) / 1000)
            
        count += len(res_list)
        if len(res_list) <= 0 or count >= settings.TASK_MAX_WRITEBACK:
            break
            

    
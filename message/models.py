# -*- coding:utf-8 -*-
import json
import random, time
from django.db import models
from celery import task
from datetime import datetime
from redis import RedisError
from django.conf import settings

#　消息
# 当前主要是IP重复或着IP变更
class Message(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'message'
    # 内容
    content = models.TextField()
    # 创建时间
    create_time = models.DateTimeField()
    # 发生时间
    occur_time = models.DateTimeField()

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
    
# message 消息回写
@task
def message_writeback():
    pipe = settings.REDIS_DB.pipeline()
    count = 0
    while True:
        item_list = []
        try:
            item_list = pop_multi(pipe, 'message', 100)
        except RedisError, e:
            # FIXME
            pass
                
        res_list = []
        for item in item_list:
            dd = json.loads(item)
            msg = Message()
            msg.content = dd['content']
            msg.create_time = datetime.now()
            msg.occur_time = dd['occur_time']
            res_list.append(msg)
        
        if res_list:
            # 对数据库进行回写
            Message.objects.bulk_create(res_list)
            
            # 队列中的记录还没有被全部回写，休眠一段时间，重复上面过程
            # 50ms ~ 200ms
            sleep_time = random.randint(50, 200)
            time.sleep(float(sleep_time) / 1000)
            
        count += len(res_list)
        if len(res_list) <= 0 or count >= settings.TASK_MAX_WRITEBACK:
            break

    
    
    
    
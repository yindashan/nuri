# -*- coding:utf-8 -*-
import random, time
import json
from celery import task
from django.db import models
from redis import RedisError
from django.conf import settings

# 监控点
# 应用-主机-监控项的组合就是监控点
class MonitorPoint(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'monitor_point'
    
    # 应用名称
    appname = models.CharField(max_length=64)
    # 主机
    host = models.CharField(max_length=32)
    # 监控项ID
    mid = models.IntegerField()
    # 是否有效 0:无效 1:有效
    is_valid = models.IntegerField()
    
    def __eq__(self, other):
        if self.appname == other.appname and \
            self.host == other.host and \
            self.mid == other.mid:
            return True
        else:
            return False
        
    def __hash__(self):
        temp = self.appname + ';' + self.host 
        temp += ';' + str(self.mid)
        return hash(temp)  
    
# 监控点数据
class PointData(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'point_data'
    
    # 时间（表示某个时间区间的开始时间) 
    time = models.DateTimeField()
    point_id = models.IntegerField()
    value = models.FloatField()
    # 步长,　聚合点的类型
    step = models.IntegerField()
    
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
        
# 监控点数据回写
@task
def point_data_writeback():
    pipe = settings.REDIS_DB.pipeline()
    count = 0
    while True:
        item_list = []
        try:
            item_list = pop_multi(pipe, 'point_data', settings.MAX_RETURN_COUNT)
        except RedisError, e:
            # FIXME
            pass
                
        res_list = []
        for item in item_list:
            dd = json.loads(item)
            pd = PointData()
            pd.time = dd['time']
            pd.point_id = dd['point_id']
            pd.value = dd['value']
            pd.step = dd['step']
            res_list.append(pd)
        
        if res_list:
            # 对数据库进行回写
            PointData.objects.bulk_create(res_list)
            
            # 队列中的记录还没有被全部回写，休眠一段时间，重复上面过程
            # 50ms ~ 200ms
            sleep_time = random.randint(50, 200)
            time.sleep(float(sleep_time) / 1000)
            
        count += len(res_list)
        if len(res_list) <= 0 or count >= settings.TASK_MAX_WRITEBACK:
            break
    

        

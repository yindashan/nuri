# -*- coding: utf-8 -*-

import datetime

from django.db import models
from celery import task
from django.conf import settings

from appitem.models import AppService
from monitoritem.models import MonitorItem
from monitorpoint.models import MonitorPoint, PointData

# 监控指数需要用到的监控项
class MonitorIndexItem(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'monitor_index_item'
    # 所属应用
    app = models.ForeignKey(AppService)
    # 所属监控项
    monitor = models.ForeignKey(MonitorItem)
    # 计算方法（0：均值，1：最大值，2：最小值。默认为均值）
    calc_method = models.IntegerField(default=0)
    # 指标上限（默认为-1：无上限）
    ceiling = models.IntegerField(default=-1)
    # 权重（默认为1，暂不开放该功能）
    weight = models.IntegerField(default=1)
    # 是否有效（0：无效，1：有效。默认为有效）
    is_valid = models.IntegerField(default=1)
    # 描述
    desc = models.CharField(max_length=128)

# 每日监控指数（各项值及最终得分）
class MonitorIndexData(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'monitor_index_data'
    # 主机
    host = models.CharField(max_length=32)
    # 监控日期（格式为0000-00-00）
    monitor_date = models.DateField(u'监控日期', db_index=True)
    # 监控指数项键（0：最终得分，其余数字为monitor_index_item的ID）
    key = models.IntegerField()
    # 监控指数项键
    value = models.FloatField()

# 每日监控健康指数计算的定时任务
@task
def monitor_index_calculate():
    # 取得昨天的数据
    yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
    yesterday = yesterday.replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
    today = yesterday + datetime.timedelta(days=1)
    point_data = PointData.objects.filter(time__gte=yesterday, time__lt=today)
    
    # 删除昨天的数据，防止重复导入
    to_be_deleted = MonitorIndexData.objects.filter(monitor_date__gte=yesterday, monitor_date__lt=today)
    to_be_deleted.delete()
    
    # 获取主机列表
    try:
        app_service = AppService.objects.get(app_name="HOST_STATUS")
        host_list = (app_service.host_list).split(',')
    except:
        host_list = []
    
    # 获取监控指数列表
    monitor_index_list = MonitorIndexItem.objects.filter(is_valid=1)

    # 写回到数据库的列表
    res_list = []
    
    for host in host_list:
        health_score = 0.0
        monitor_index_num = 0
        
        for monitor_index in monitor_index_list:
            app_name = monitor_index.app.app_name
            monitor_id = monitor_index.monitor.id
            calc_method = monitor_index.calc_method
            ceiling = monitor_index.ceiling
            monitor_index_id = monitor_index.id
            #monitor_index_desc = monitor_index.desc
            
            point = MonitorPoint.objects.filter(appname=app_name).filter(mid=monitor_id).filter(host=host).filter(is_valid=1)
            if list(point) != []:
                point_id = point[0].id
                
                if calc_method == 0:
                    value = point_data.filter(point_id=point_id).aggregate(models.Avg('value'))['value__avg']
                elif calc_method == 1:
                    value = point_data.filter(point_id=point_id).aggregate(models.Max('value'))['value__max']
                elif calc_method == 2:
                    value = point_data.filter(point_id=point_id).aggregate(models.Min('value'))['value__min']
            else:
                value = None
            
            # 写入列表
            temp_index_data = MonitorIndexData()
            temp_index_data.host = host
            temp_index_data.monitor_date = yesterday
            temp_index_data.key = monitor_index_id
            temp_index_data.value = value if value is not None else -1
            res_list.append(temp_index_data)
            
            # 加入分数（未来可能加入权重计算）
            monitor_index_num += 1
            if value is None:
                health_score += 0.0
            else:
                if ceiling == -1:
                    health_score += 100.0 / (1 + 0.1 * value)
                else:
                    health_score += 100.0 * (ceiling - value) / ceiling
        
        # 计算每个host的最终健康指数，并写入列表
        health_score /= monitor_index_num
        temp_index_data = MonitorIndexData()
        temp_index_data.host = host
        temp_index_data.monitor_date = yesterday
        temp_index_data.key = 0
        temp_index_data.value = health_score
        res_list.append(temp_index_data)

    # 写回到数据库
    if res_list:
        MonitorIndexData.objects.bulk_create(res_list)

# 获取监控指数的“id-描述”对应字典
def get_monitor_index_dict():
    monitor_index_dict = {}
    monitor_index_items = MonitorIndexItem.objects.filter(is_valid=1)
    for item in monitor_index_items:
        monitor_index_dict[item.id] = item.desc
    return monitor_index_dict

# 从redis获取主机IP列表
def get_host_ip_list(monitor_index_data):
    pipe = settings.REDIS_DB.pipeline()
    for line in monitor_index_data:
        pipe.hget("host_ip", line['host'])
    host_list = pipe.execute()
    return host_list
    
    
# -*- coding:utf-8 -*-
from monitorpoint.models import MonitorPoint
from monitoritem.models import app_mitem
from appitem.models import AppRelation
from redissync.models import sync_app_mpoint

# 根据配置修改监控点信息
def sync_monitor_point(app):
    # 1) 修改数据库
    sync_mpoint_db(app)
    # 2) 同步redis
    sync_app_mpoint(app)


# 根据配置修改监控点信息, 变更数据库    
def sync_mpoint_db(app):
    # 1) 此应用所拥有的监控点
    old_point_list = MonitorPoint.objects.filter(appname=app.app_name, is_valid=1)
    old_set = set(old_point_list)
        
    # 2) 配置变更后，此应用所拥有的监控点
    mitem_list = app_mitem(app)
    new_set = set()
    for host in app.host_list.split(','):
        for mitem in mitem_list:
            mp = MonitorPoint()
            mp.appname = app.app_name
            mp.host = host
            mp.mid = mitem.id
            mp.is_valid = 1
            new_set.add(mp)
    
    # 3) 变更
    # 创建监控点
    cpoint_list = list(new_set - old_set)
    # 批量插入
    MonitorPoint.objects.bulk_create(cpoint_list)
            
    # 删除监控点(仅置位)
    dhost_set = set()
    dmid_set = set()
    for item in (old_set - new_set):
        dhost_set.add(item.host)
        dmid_set.add(item.mid)
        
    MonitorPoint.objects.filter(appname=app.app_name, \
        host__in=dhost_set, mid__in=dmid_set).update(is_valid=0)
        
    # 如果当前应用有子应用，则重新计算每个子应用的监控项
    rel_list = AppRelation.objects.filter(parent_app=app)
    for rel in rel_list:
        sync_mpoint_db(rel.child_app)

        
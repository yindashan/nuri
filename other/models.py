# -*- coding:utf-8 -*-
from celery import task
from appitem.models import AppService
from monitorpoint.logic import sync_monitor_point
from utils.utils import filterIP
from message.models import Message
from datetime import datetime
from redissync.models import get_ip
from django.conf import settings
from redissync.models import sync_app_info

# 主机自动发现
# 只增加主机，不删除
@task
def host_auto_find():
    # 通过硬件检查结果得到
    key_list = settings.REDIS_DB.keys("GD*_hc")
    host_list = [ key.split('_')[0] for key in key_list ]
    new_host_set = set(host_list)
    
    host_list = settings.REDIS_DB.get("all_host_list")
    if host_list is None:
        host_list = []
    else:
        host_list = host_list.split(',')
    old_host_set = set(host_list)
    
    margin_set = new_host_set - old_host_set
    
    app = AppService.objects.get(app_name='HOST_STATUS')
    
    if margin_set:
        add_ip  = get_ip(margin_set)
        msg = Message()
        msg.create_time = datetime.now()
        msg.occur_time =  datetime.now()
        msg.content = "发现新主机, 主机ID:%s, 对应IP:%s" % (','.join(margin_set), ','.join(add_ip))
        msg.save()
        
        ip_list = []
        if  app.ip_list:
            ip_list  = app.ip_list.split(',')
        ip_list.extend(add_ip)
        app.ip_list = ','.join(filterIP(ip_list))
        
        host_list = []
        if app.host_list:
            host_list = app.host_list.split(',')
        app.host_list = ','.join( set(host_list) | margin_set )
        
        app.save()
        
        #　根据监控项变化情况，同步监控点
        sync_monitor_point(app)
        
        #　同步应用配置
        sync_app_info(app)
        
        # 变更redis    
        settings.REDIS_DB.set("all_host_list", ','.join(new_host_set))
        



    
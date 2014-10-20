# -*- coding:utf-8 -*-
from appitem.models import AppService
from redissync.models import get_ip, host2ip
from utils.utils import filterIP
from django.conf import settings

import logging


# 是否是一个合法的host_id
def valid_host_id(host_id):
    if len(host_id) == 12 and host_id[0:2] == 'GD':
        return True
    else:
        return False

# 主机下线
def host_offline(host_id):
    logger = logging.getLogger("django")
    if not valid_host_id(host_id):
        logger.error(u"主机下线--为主机下线提供的host_id不合法,%s", host_id)
        return False
    
    app_list = AppService.objects.filter(host_list__icontains=host_id)
    for app in app_list:
        host_list = app.host_list.split(',')
        host_list.remove(host_id)
        app.ip_list = ','.join(filterIP(get_ip(host_list)))
        app.host_list = ','.join(host_list)
        app.save()
    
    # 清除redis中,主机对应的硬件检查信息
    settings.REDIS_DB.delete(host_id + '_hc')
        
    # 保存下线记录
    ip = host2ip(host_id)
    logger.info(u"主机下线--host_id: %s,当前IP: %s", host_id, ip)
    return True
    
    
# 主机IP变更
def host_change_ip(host_id, old_ip, new_ip):
    logger = logging.getLogger("django")
    if not valid_host_id(host_id):
        logger.error(u"主机IP变更--为主机IP变更提供的host_id不合法,%s", host_id)
        return False
        
    app_list = AppService.objects.filter(host_list__icontains=host_id)
    for app in app_list:
        host_list = app.host_list.split(',')
        app.ip_list = ','.join(filterIP(get_ip(host_list)))
        app.host_list = ','.join(host_list)
        app.save()
        
    # 保存下线记录
    logger.info(u"主机IP变更--host_id: %s,原IP: %s,新IP", host_id, old_ip, new_ip)  
    return True
    
    
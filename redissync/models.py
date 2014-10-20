# -*- coding:utf-8 -*-

import json
import datetime
import logging
from redis import RedisError
from django.conf import settings
from appitem.models import AppService, AppRelation, gen_step_info
from monitoritem.models import app_mitem
from monitorpoint.models import MonitorPoint
from nocip.models import NOCIP
from django.db import models
from django.db import transaction

def sync_config():
    logger = logging.getLogger("django")
    try:
        # 1) 同步应用配置信息
        sync_all_app_info()
        # 2) 同步应用监控项信息
        sync_all_app_mitem()
        # 3) 同步监控点信息
        sync_all_app_mpoint()
        # 4) 同步当前已有的主机信息
        sync_all_host_info()
        # 5) 同步应用列表及检查计划
        sync_all_app_change()
        
    except RedisError, e:
        logger.error("同步应用监控配置信息失败。原因:%s", str(e) )
        return False
    logger.info("同步应用监控配置信息成功。")
    return True

# 1) 同步应用配置信息
def sync_app_info(app):
    pipe = settings.REDIS_DB.pipeline() 
    pipe.hset(app.app_name + '_config', 'storage_step', gen_step_info(app))
    pipe.hset(app.app_name + '_config', 'ip_list', app.ip_list)
    pipe.hset(app.app_name + '_config', 'host_list', app.host_list)
    pipe.hset(app.app_name + '_config', 'max_check_attempts', app.max_check_attempts)
    pipe.hset(app.app_name + '_config', 'check_interval', app.check_interval)
    pipe.hset(app.app_name + '_config', 'notify_interval', app.notify_interval)
    pipe.hset(app.app_name + '_config', 'email_list', app.email_list)
    pipe.hset(app.app_name + '_config', 'mobile_list', app.mobile_list)
    
    # 1. parent_app_list
    # 注: 当前最多只会有一个父应用
    rel_list = AppRelation.objects.filter(child_app=app)
    parent_list = []
    for rel in rel_list:
        parent_name = rel.parent_app.app_name
        parent_list.append(parent_name)
               
    # 修改本应用的parent_app_list
    if parent_list:
        pipe.hset(app.app_name + '_config', 'parent_app_list', ','.join(parent_list))
    else:
        pipe.hdel(app.app_name + '_config', 'parent_app_list')
    
    pipe.execute()

    # ----------- 额外逻辑 ----------
    # 如果app的类型是host_status
    host_list = app.host_list.split(',')
    if app.type == 5:
        for host in host_list:
            pipe.hget('_hs_host_app', host)
            
        result_list = pipe.execute()
        
        for i in range(len(host_list)):
            if result_list[i]:
                temp = set(result_list[i].split(','))
                temp.add(app.app_name)
            else:
                temp = [app.app_name]
	    print temp
	    print host_list[i], ','.join(temp)
            pipe.hset('_hs_host_app', host_list[i], ','.join(temp))
    
    pipe.execute()

def sync_all_app_info():
    app_list = AppService.objects.all()
    for app in app_list:
        sync_app_info(app)

# 2) 同步应用的监控项信息(监控规则)
def sync_app_mitem(app):
    # 获取应用所用的监控项，包含从父应用继承的
    mitem_list = app_mitem(app)
    
    rules = []
    for item in mitem_list:
        temp = {}
        temp['id'] = item.id
        temp['monitor_type'] = item.monitor_type
        temp['var_name'] = item.var_name
        temp['formula'] = item.formula
        temp['warning_threshold'] = item.warning_threshold
        temp['critical_threshold'] = item.critical_threshold
        temp['desc'] = item.desc
        rules.append(temp)
    
    settings.REDIS_DB.hset('app_rules', app.app_name, json.dumps(rules))
    
    # 如果当前应用有子应用，则重新计算每个子应用的监控项
    rel_list = AppRelation.objects.filter(parent_app=app)
    for rel in rel_list:
        sync_app_mitem(rel.child_app)
        
def sync_all_app_mitem():
    # 速度可能会受到影响
    app_list = AppService.objects.all()
    for app in app_list:
        sync_app_mitem(app)

# 3) 同步监控点信息
def sync_app_mpoint(app):
    pipe = settings.REDIS_DB.pipeline()
    
    mp_list = MonitorPoint.objects.filter(appname=app.app_name, is_valid = 0)
    for mp in mp_list:
        # 注意: mid　是监控项ID
        pipe.hdel('monitor_point', mp.appname + '_' + mp.host + '_' + str(mp.mid))
        # 删除无用的监控点缓存数据
        for step in [1, 5, 30, 360]:
            key_starttime = "mp_%d_%d_starttime" % (mp.id, step)
            pipe.delete(key_starttime)
            
            key_list = "mp_%d_%d_list" % (mp.id, step)
            pipe.delete(key_list)
        
        
    
    point_list = MonitorPoint.objects.filter(appname=app.app_name, is_valid = 1)
    for point in point_list:
        pipe.hset('monitor_point', point.appname + '_' + point.host + '_' + str(point.mid), str(point.id)) 
      
    # 不支持这种方式的批量删除
    # pipe.hdel('monitor_point', field_list)
    
    pipe.execute()  
    
    # 如果当前应用有子应用，则重新计算每个子应用的监控项
    rel_list = AppRelation.objects.filter(parent_app=app)
    for rel in rel_list:
        sync_app_mpoint(rel.child_app)
     
def sync_all_app_mpoint():
    pipe = settings.REDIS_DB.pipeline()
    
    mp_list = MonitorPoint.objects.filter(is_valid = 0)
    for mp in mp_list:
        # 注意: mid　是监控项ID
        pipe.hdel('monitor_point', mp.appname + '_' + mp.host + '_' + str(mp.mid))
        # 删除无用的监控点缓存数据
        for step in [1, 5, 30, 360]:
            key_starttime = "mp_%d_%d_starttime" % (mp.id, step)
            pipe.delete(key_starttime)
            
            key_list = "mp_%d_%d_list" % (mp.id, step)
            pipe.delete(key_list)
    
    # 不支持这种方式的批量删除
    # pipe.hdel('monitor_point', field_list)
    
    point_list = MonitorPoint.objects.filter(is_valid = 1)
    for point in point_list:
        pipe.hset('monitor_point', point.appname + '_' + point.host + '_' + str(point.mid), str(point.id))  
    
    pipe.execute()     

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

# 如果host不存在, 会自动创建一个伪造的host_id 
# 形如: FK1200000000
def get_host(ip_list):
    pipe = settings.REDIS_DB.pipeline()
    
    host_list = []
    for ip in ip_list:
        pipe.hget('ip_host', ip)
    
    item_list = pipe.execute()
    for i in range(len(item_list)):
        item = item_list[i]
        if not item:
            item  = gen_fake_host_id()
            # 保存至数据库
            pipe.hset('ip_host', ip_list[i], item)
            pipe.hset(item + '_hc', 'IP', ip_list[i])
            pipe.hset("host_ip", item, ip_list[i])
            
        host_list.append(item)
    pipe.execute()   
    return host_list
        
def get_ip(host_list):
    pipe = settings.REDIS_DB.pipeline()
    
    ip_list = []
    for host in host_list:
        pipe.hget("host_ip", host)
        
    item_list = pipe.execute()
    for item in item_list:
        if item:
            ip_list.append(item)
    return ip_list

# 不过滤ip为None的情况
def get_all_ip(host_list):
    pipe = settings.REDIS_DB.pipeline()
    
    for host in host_list:
        pipe.hget("host_ip", host)
        
    item_list = pipe.execute()
    return item_list

# 从redis中移除与应用相关的所有配置信息
def remove_app_info(app):
    pipe = settings.REDIS_DB.pipeline() 
    
    # 删除应用配置信息 
    pipe.delete(app.app_name +  '_config')
    
    # 删除应用的监控规则
    pipe.hdel('app_rules', app.app_name)
    
    # 删除应用关联的监控点信息
    field_list = []
    
    mp_list = MonitorPoint.objects.filter(appname=app.app_name)
    for mp in mp_list:
        field_list.append(mp.appname + '_' + mp.host + '_' + str(mp.mid))
    
    pipe.hdel('monitor_point', field_list)
    
    pipe.execute()
    
    # 删除应用对应的时间戳和跟主动监控有关的配置信息
    remove_app_info_config(app)


def remove_app_info_config(app):
    """
    从redis中移除应用对应的时间戳和跟主动监控有关的配置信息
    """
    if app.type == 1: # Http类型
        hashkey_timestamp = 'http_url_timestamp'
    elif app.type == 2: # Ping类型
        hashkey_timestamp = 'ping_server_timestamp'
    elif app.type == 3: # TCP类型
        hashkey_timestamp = 'tcp_port_timestamp'
    else: # 其他应用类型
        hashkey_timestamp = 'other_app_timestamp'
    
    # 删除时间戳信息
    is_hashkey_timestamp = settings.REDIS_DB.exists(hashkey_timestamp)
    if is_hashkey_timestamp:
        is_app_field_timestamp = settings.REDIS_DB.hexists(hashkey_timestamp, app.app_name)
        if is_app_field_timestamp:
            settings.REDIS_DB.hdel(hashkey_timestamp, app.app_name)
    
    if app.type == 1: # Http类型
        hashkey_config = 'http_url_configuration'
    elif app.type == 3: # TCP类型
        hashkey_config = 'tcp_port_configuration'
        
    # 删除跟主动监控有关的配置信息
    is_hashkey_config = settings.REDIS_DB.exists(hashkey_config)
    if is_hashkey_config:
        is_app_field_config = settings.REDIS_DB.hexists(hashkey_config, app.app_name)
        if is_app_field_config:
            settings.REDIS_DB.hdel(hashkey_config, app.app_name)
    
    
# 主机ID转换为IP地址   
def host2ip(host):
    return settings.REDIS_DB.hget("host_ip", host)
    
    
# IP地址转换为主机ID   
def ip2host(ip):
    return settings.REDIS_DB.hget('ip_host', ip)
    
    
def update_app_timestamp(app):
    """
    根据应用类型更新相应应用对应的时间戳
    """
    if app.type == 1: # Http类型
        key = 'http_url_timestamp'
    elif app.type == 2: # Ping类型
        key = 'ping_server_timestamp'
    elif app.type == 3: # TCP类型
        key = 'tcp_port_timestamp'
    else: # 其他应用类型
        key = 'other_app_timestamp'
    settings.REDIS_DB.hset(key, app.app_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))


def update_timestamp_by_app_and_type(app_name, app_type):
    """
    根据应用名称和应用类型更新时间戳
    """
    if app_type == 'http': # Http类型
        key = 'http_url_timestamp'
    elif app_type == 'ping': # Ping类型
        key = 'ping_server_timestamp'
    elif app_type == 'tcp': # TCP类型
        key = 'tcp_port_timestamp'
    else: # 其他应用类型
        key = 'other_app_timestamp'
    settings.REDIS_DB.hset(key, app_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    
    
def update_timestamp_by_nocid(nocid):
    """
    更新当前机房下所有应用对应的时间戳
    """
    hash_key = "noc_app_map_" + nocid
    is_hashkey = settings.REDIS_DB.exists(hash_key)
    if is_hashkey:
        # http应用信息,key为：http
        is_http_field = settings.REDIS_DB.hexists(hash_key, 'http')
        if is_http_field:
            app_http_list = settings.REDIS_DB.hget(hash_key, 'http').split(',')
            for appname in app_http_list:
                update_timestamp_by_app_and_type(appname, 'http')
                
        # ping应用信息,key为：ping
        is_http_field = settings.REDIS_DB.hexists(hash_key, 'ping')
        if is_http_field:
            app_http_list = settings.REDIS_DB.hget(hash_key, 'ping').split(',')
            for appname in app_http_list:
                update_timestamp_by_app_and_type(appname, 'ping')
                
        # tcp应用信息,key为：tcp
        is_http_field = settings.REDIS_DB.hexists(hash_key, 'tcp')
        if is_http_field:
            app_http_list = settings.REDIS_DB.hget(hash_key, 'tcp').split(',')
            for appname in app_http_list:
                update_timestamp_by_app_and_type(appname, 'tcp')
                
        # 其他应用信息,key为：other
        is_http_field = settings.REDIS_DB.hexists(hash_key, 'other')
        if is_http_field:
            app_http_list = settings.REDIS_DB.hget(hash_key, 'other').split(',')
            for appname in app_http_list:
                update_timestamp_by_app_and_type(appname, 'other')
    
    
        



def remove_noc_app_map(app):
    """
    删除noc_app_map_*中该应用相关的信息
    """
    if app.type == 1: # Http类型
        key = 'http'
    elif app.type == 2: # Ping类型
        key = 'ping'
    elif app.type == 3: # TCP类型
        key = 'tcp'
    else: # 其他应用类型
        key = 'other'
    
    for nocid in app.noc_list.split(','):
        hash_key = "noc_app_map_" + nocid
        is_hashkey = settings.REDIS_DB.exists(hash_key)
        if is_hashkey:
            isfield = settings.REDIS_DB.hexists(hash_key, key)
            if isfield:
                appname_list_tmp = settings.REDIS_DB.hget(hash_key, key).split(',')
                new_appname_list_tmp = [appname for appname in appname_list_tmp if appname != app.app_name]
                if new_appname_list_tmp:
                    settings.REDIS_DB.hset(hash_key, key, ','.join(new_appname_list_tmp))
                else:
                    settings.REDIS_DB.hdel(hash_key, key)

    
def add_noc_app_map(app):
    """
    添加noc_app_map_*中该应用相关的信息
    """
    
    if app.type == 1: # Http类型
        key = 'http'
    elif app.type == 2: # Ping类型
        key = 'ping'
    elif app.type == 3: # TCP类型
        key = 'tcp'
    else: # 其他应用类型
        key = 'other'
        
    for nocid in app.noc_list.split(','):
        """
        查看是否存在键值:
        redis_db.exists('template_21')  #看是否存在这个键值
        
        查看哈希表 key 中，给定域 field 是否存在。
        如果哈希表含有给定域，返回 1 。
        如果哈希表不含有给定域，或 key 不存在，返回 0 。
        """
        
        hash_key = "noc_app_map_" + nocid
        is_hashkey = settings.REDIS_DB.exists(hash_key)
        
        if is_hashkey:
            isfield = settings.REDIS_DB.hexists(hash_key, key)
            if isfield:
                field_value_list = settings.REDIS_DB.hget(hash_key, key).split(',')
                if app.app_name not in field_value_list:
                    field_value_list.append(app.app_name)
                    settings.REDIS_DB.hset(hash_key, key, ','.join(field_value_list))
            else:
                settings.REDIS_DB.hset(hash_key, key, app.app_name)
        else:
            settings.REDIS_DB.hset(hash_key, key, app.app_name)


def update_noc_app_map(app, noc_list_tmp):
    """
    更新noc_app_map_*中该应用相关的信息
    """
    # 应该存在当前应用的机房
    app_nocid_list = app.noc_list.split(',')
    # 原来应用对应的机房编号列表为noc_list_tmp，计算得出不应该存在当前应用的机房
    nocid_list_tmp = [nocid for nocid in noc_list_tmp if nocid not in app_nocid_list]
    
    if app.type == 1: # Http类型
        key = 'http'
    elif app.type == 2: # Ping类型
        key = 'ping'
    elif app.type == 3: # TCP类型
        key = 'tcp'
    else: # 其他应用类型
        key = 'other'
    
    # 应该存在当前应用的机房
    for nocid in app_nocid_list:
        """
        查看哈希表 key 中，给定域 field 是否存在。
        如果哈希表含有给定域，返回 1 。
        如果哈希表不含有给定域，或 key 不存在，返回 0 。
        """
        hash_key = "noc_app_map_" + nocid
        is_hashkey = settings.REDIS_DB.exists(hash_key)
        if is_hashkey:
            isfield = settings.REDIS_DB.hexists(hash_key, key)
            if isfield:
                field_value_list = settings.REDIS_DB.hget(hash_key, key).split(',')
                if app.app_name not in field_value_list:
                    field_value_list.append(app.app_name)
                    settings.REDIS_DB.hset(hash_key, key, ','.join(field_value_list))
            else:
                settings.REDIS_DB.hset(hash_key, key, app.app_name)
        else:
            settings.REDIS_DB.hset(hash_key, key, app.app_name)
    
    # 不应该存在当前应用的机房
    for nocid_tmp in nocid_list_tmp:
        hash_key = "noc_app_map_" + nocid_tmp
        is_hashkey = settings.REDIS_DB.exists(hash_key)
        if is_hashkey:
            isfield = settings.REDIS_DB.hexists(hash_key, key)
            if isfield:
                appname_list_tmp = settings.REDIS_DB.hget(hash_key, key).split(',')
                new_appname_list_tmp = [appname for appname in appname_list_tmp if appname != app.app_name]
                if new_appname_list_tmp:
                    settings.REDIS_DB.hset(hash_key, key, ','.join(new_appname_list_tmp))
                else:
                    settings.REDIS_DB.hdel(hash_key, key)


def maintain_noc_ip_map(nocid):
    """
    维护noc_ip_map信息
    """
    nocips = NOCIP.objects.filter(nocid__iexact=nocid)
    if nocips:
        ip_list = [nocip.ip for nocip in nocips]
        settings.REDIS_DB.hset('noc_ip_map', nocid, ','.join(ip_list))
    else:
        settings.REDIS_DB.hdel('noc_ip_map', nocid)
    
    


def maintain_http_url_configuration(app):
    """
    维护redis中http_url_configuration信息
    """
    return_list = []
    urlinfo_list = app.urlinfo_set.all().filter(is_deleted=1)
    for urlinfo in urlinfo_list:
        item = {}
        item['url_id'] = urlinfo.id
        item['url_value'] = urlinfo.url
        if urlinfo.responsetime != None and urlinfo.responsetime != '':
            item['responsetime'] = urlinfo.responsetime
        if urlinfo.type != None and urlinfo.type != '' and urlinfo.target != None and urlinfo.target != '' and urlinfo.value != None and urlinfo.value != '':
            item['type'] = urlinfo.type
            item['target'] = urlinfo.target
            item['value'] = urlinfo.value
        return_list.append(item)
        
    if return_list:
        settings.REDIS_DB.hset('http_url_configuration', app.app_name, json.dumps(return_list))
    else:
        settings.REDIS_DB.hdel('http_url_configuration', app.app_name)
    
# 存储伪造的ID号
class Number(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'fake_number'
    number = models.IntegerField()
    
# 创建伪造的host_id
# host_id 形如 FK1200000000
@transaction.commit_on_success
def gen_fake_host_id():
    limit = 10
    item = Number.objects.select_for_update().get(id=1)
    item.number = item.number + 1
    item.save()
    
    num = str(item.number)
    for i in range(limit - len(num)):
        num = '0' + num
    return 'FK' + num
        
# 同步主机信息
def sync_all_host_info():
    host_list = []
    app = AppService.objects.get(app_name='HOST_STATUS')
    host_list.extend(app.host_list.split(','))
    rel_list = AppRelation.objects.filter(parent_app=app)
    for rel in rel_list:
        temp = rel.child_app.host_list 
        if temp:
            host_list.extend(temp.split(','))
            
    settings.REDIS_DB.set('all_host_list', ','.join(host_list))
    
    
def maintain_tcp_port_configuration(app):
    """
    维护redis中tcp_port_configuration信息
    """
    return_list = []
    tcpinfo_list = app.tcpinfo_set.all()
    for tcpinfo in tcpinfo_list:
        item = {}
        item['port'] = tcpinfo.port
        if tcpinfo.responsetime != None and tcpinfo.responsetime != '':
            item['responsetime'] = tcpinfo.responsetime
        return_list.append(item)
        
    if return_list:
        settings.REDIS_DB.hset('tcp_port_configuration', app.app_name, json.dumps(return_list))
    else:
        settings.REDIS_DB.hdel('tcp_port_configuration', app.app_name)

# 当前应用发生变化时，重置应用对应的检查计划
def sync_app_change(app):
    sync_app_list()
    settings.REDIS_DB.rpush('_app_change_list', app.app_name)

# # 重置所有应用对应的检查计划
def sync_all_app_change():
    # 同步应用列表
    sync_app_list()
    
    pipe = settings.REDIS_DB.pipeline()
    app_list = AppService.objects.all()
    for app in app_list:
        pipe.rpush('_app_change_list', app.app_name)
    pipe.execute()
    
# 同步应用列表
def sync_app_list():
    app_list = AppService.objects.all()
    app_list = [app.app_name for app in app_list]
    settings.REDIS_DB.set('_all_app_list', ','.join(app_list))
    



    

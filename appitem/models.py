# -*- coding:utf-8 -*-
from django.db import models
from authority.models import Permission
from utils.constants import noc_info_dict, app_type_dict

# 应用服务
# 父子应用关系只能有两级
class AppService(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'app_service'
    # 应用名称
    app_name = models.CharField(max_length=64,unique = True)
    # 关于此应用的描述
    desc = models.CharField(max_length=128)
    # 应用所在主机的IP地址列表，以逗号分隔  
    # 形如：192.168.1.122,10.2.161.51,192.168.1.110
    ip_list = models.TextField()
    
    # IP对应的主机ID列表,以逗号分隔  
    host_list = models.TextField()
    
    # 邮件列表
    email_list = models.CharField(max_length = 255)
    # 手机列表
    mobile_list = models.CharField(max_length = 255)
    # 是否报警　0:不报警,1:报警
    is_alarm = models.IntegerField(default=0)
    
    # 检查时间间隔 (单位:分钟)
    check_interval = models.IntegerField(default=5)
    
    # 最大检查次数 决定应用是否达到 hard state (连续几次检查都超过阀值才会触发报警)
    max_check_attempts = models.IntegerField(default=2)
    
    # 决定数据监控点数据如何存储
    # 逗号分隔 形如 5,30,360
    step_list = models.CharField(max_length=128)
    
    # 机房分布信息
    noc_list = models.CharField(max_length=255)
    
    # 应用项类型
    # 1:'Http', 2:'Ping', 3:'TCP', 4:'其它'
    type = models.IntegerField(default=4)
    
    # 通知间隔　单位: 分钟
    # 注: 上次通知和当前之间的差值如果小于此值, 就不触发报警
    notify_interval = models.IntegerField(default=60)

# 用于前台的展现    
class AppRepr(object):
    def __init__(self, app):
        self.id = app.id
        self.app_name = app.app_name
        self.desc = app.desc
        self.host_count = 0
        # 当前主机数量
        if app.host_list:
            self.host_count = len(app.host_list.split(','))
        # 父应用
        rel_list = AppRelation.objects.filter(child_app=app)
        temp_list = []
        for rel in rel_list:
            temp_list.append(rel.parent_app.app_name)
        self.parent_app_list = ','.join(temp_list)
        self.is_alarm = app.is_alarm
        # 是否允许创建子应用
        # 注:当前只允许创建2级的父子关系
        self.is_child_app = True
        rel_list = AppRelation.objects.filter(child_app=app)
        if rel_list:
            self.is_child_app = False
            
        # 应用部署机房
        idc_list = []
        for noc in app.noc_list.split(','):
            if noc:
                idc_list.append(noc_info_dict[noc])
                
        self.idc_list = ','.join(idc_list)
        
        # 类型
        self.type = app_type_dict[app.type]
        
# 维护应用的应用之间的关系    
class AppRelation(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'app_relation'
    
    parent_app = models.ForeignKey(AppService, related_name='parent_app_id') 
    
    child_app = models.ForeignKey(AppService, related_name='child_app_id') 
    
# app_name 转换成对应的监控项权限字段
# 表示对此应用下的监控项有操作的权限
def app2AuthStr(app_name):
    return app_name + '_monitor_operate'  

# 应用对应的权限记录    
def create_perm_record(app_name):
    # 创建对应的权限记录 此应用监控项的读和操作权限
    newpm = Permission();
    newpm.codename = app2AuthStr(app_name)
    newpm.desc = app_name + u"管理权限"
    newpm.type=3
    newpm.save()
    
# 返回可以操作的应用ID列表  
def managable_app_id(auth_set):
    res_list = []
    app_list = AppService.objects.all()
    for app in app_list:
        if app2AuthStr(app.app_name) in  auth_set:
            res_list.append(app.id)
    
    return res_list
    
# 返回可以操作的应用ID列表  
def managable_app(auth_set):
    res_list = []
    app_list = AppService.objects.all()
    for app in app_list:
        if app2AuthStr(app.app_name) in  auth_set:
            res_list.append(app)
    
    return res_list
    
# 聚合点步长信息
def gen_step_info(app):
    step_list = [1, 5, 30, 360]
    res_list = []
    for step in step_list:
        if step >= app.check_interval:
            res_list.append(str(step))  
    return ','.join(res_list)

# -*- coding:utf-8 -*-
from appitem.models import AppRelation, AppService
from authority.models import Permission
from redissync.models import remove_app_info, remove_noc_app_map, sync_app_change
from django.conf import settings
from monitorpoint.models import MonitorPoint
from appitem.models import app2AuthStr

# 保存父子关系
def save_pc_rel(app, parent_id):
    if  parent_id != -1:
        rel = AppRelation()
        rel.parent_app = AppService.objects.get(id=parent_id)
        rel.child_app = app
        rel.save()
        
def remove_app(app):
    # 删除父子关系及子应用  
    remove_pc_rel(app)
    
    #删除应用对应的监控项
    mitems = app.monitoritem_set.all()
    mitems.delete()
    
    app.delete()
    
    # 删除此应用对应的权限字段
    Permission.objects.get(codename=app2AuthStr(app.app_name)).delete()
    
    # 删除监控点
    MonitorPoint.objects.filter(appname=app.app_name, is_valid=1).update(is_valid = 0)
    
    # 从redis中移除应用的所有相关信息
    remove_app_info(app)
    
    # 删除noc_app_map中该应用相关的信息
    remove_noc_app_map(app)    
    
    # 同步应用检查计划
    sync_app_change(app)
    
# 删除父子关系及子应用
def remove_pc_rel(app):
    # 父子(app为父应用)
    rel_list = AppRelation.objects.filter(parent_app_id=app.id)
    for rel in rel_list:
        remove_app(rel.child_app)
        
    rel_list.delete()
    # 子父(app为子应用)
    rel_list = AppRelation.objects.filter(child_app_id=app.id)
    rel_list.delete()
            

            
            
            
# -*- coding:utf-8 -*-
import re
from django.db import models
from appitem.models import AppService, AppRelation

# 监控项
class MonitorItem(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'monitor_item'
    # 类型 1:单个变量 2:计算公式
    monitor_type = models.IntegerField()
    # 如果属于类型为A类用此值
    var_name = models.CharField(max_length=32,null=True)
    # 如果属于B类用此公式
    formula = models.CharField(max_length=255,null=True)
    # 警告阀值
    warning_threshold = models.CharField(max_length=32)
    # 错误阀值
    critical_threshold = models.CharField(max_length=32)
    # 描述
    desc = models.CharField(max_length = 1000)
    
    #外键  应用服务
    app = models.ForeignKey(AppService) # 多对一关联

    def clone(self):
        item = MonitorItem()
        item.monitor_type = self.monitor_type
        item.var_name = self.var_name
        item.formula = self.formula
        item.warning_threshold = self.warning_threshold
        item.critical_threshold = self.critical_threshold
        item.desc = self.desc
        item.app = self.app
        
        return item

class MITemp(object):
    def __init__(self, mid, desc):
        self.id = mid
        self.desc = desc

def monitorItem2Temp(mitem_list):
    res_list = []
    for item in mitem_list:
        m = MITemp(item.id, item.desc)
        res_list.append(m)
    return res_list
    
# 根据页面传递的类型和参数值生成nagios可识别的字符串
def generate_threshold(threshold_type,t,t1,t2):
    if threshold_type=='1':
        return '~:' + t
    elif threshold_type=='2':
        return t + ':'
    elif threshold_type=='3':
        return '@'+ t1 + ':' + t2
    else:
        return t1 + ':' + t2
        
# 根据nagios可识别的字符串，生成一个元组(threshold_type,t,t1,t2)
# 如果其中一个值不存在，则返回None
# threshold_type 如下:
# 1) x > t 
# 2) x < t   
# 3) t1 <= x <= t2  
# 4) x < t1 或　x > t2
def parse_threshold(threshold_str):
    t = None
    t1 = None
    t2 = None
    pattern_list = ['^~:([\d|\.]+)$','^([\d|\.]+):$','^@([\d|\.]+):([\d|\.]+)$','^([\d|\.]+):([\d|\.]+)$']
    for i in range(4):
        res = re.match(pattern_list[i],threshold_str)
        if res is not None:
            if i==0 or i==1:
                #print 'all:',res.groups()
                t = res.group(1)
            else:
                #print 'all:',res.groups()
                t1 = res.group(1)
                t2 = res.group(2)
            return (i+1,t,t1,t2)
        
    return None

# 取得一个应用的所有监控项
# 受到继承关系的影响
def app_mitem(app):
    all_list = []
    # 获取自己的父应用--单继承
    rel_list = AppRelation.objects.filter(child_app=app)
    for item in rel_list:
        mitem_list = item.parent_app.monitoritem_set.all()
        all_list.extend(mitem_list)
        
    all_list.extend(app.monitoritem_set.all())
    
    dd = {}  
    # 子应用中如果有与父应用中同名的监控项则覆盖父应用的监控项
    for mitem in all_list:
        # 单个变量
        if mitem.monitor_type == 1:
            dd[mitem.var_name] = mitem
        # 计算公式
        else:
            dd[mitem.formula] = mitem
            
    res_list = []
    for key in dd:
        res_list.append(dd[key])
        
    return res_list
    
    



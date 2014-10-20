# -*- coding:utf-8 -*-
from datetime import datetime

# 用户自定义类    
def obj2dict(obj):
    dd = {}
    # 展开它的属性
    for m in dir(obj):
        if m[0] != "_" :
            value = getattr(obj, m)
            if not callable(value):
                dd[m] = complexObj2json(value)
    return dd
    
def list2json(ll):
    res_list = []
    for item in ll:
        value = complexObj2json(item)      
        res_list.append(value)  
    return res_list 
    
def dict2json(dd):
    res = {}
    for item in dd:
        res[item] = complexObj2json(dd[item])
    return res
    
# complex obj to json
# 复杂对象转换json对象 (dict、list)
def complexObj2json(obj):
    # list, set, tuple
    if isinstance(obj,(list, set, tuple)):
        return list2json(obj)
    # dict
    elif isinstance(obj,dict):
        return dict2json(obj)
    # 基本类型
    # int, long, basestring, bool, float
    elif obj == None or isinstance(obj, (int, long, basestring, bool, float)):
        return obj
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    # 用户自定义的类
    else:
        return obj2dict(obj)
        
        

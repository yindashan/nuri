# -*- coding:utf-8 -*-
from django import template  #导入模板包
register = template.Library()  #register 的模块级变量，template.Library的实例

@register.filter('my_truncate')
def my_truncate(value, arg=10):
    max_length = int(arg)
    if len(value) > max_length:
        return value[0:max_length] + '...'
    else:
        return value
    



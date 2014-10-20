# -*- coding:utf-8 -*-
# ErrorCode 101   ------>  没有找到对应的数据源
from django.shortcuts import render_to_response, _get_queryset
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.utils import simplejson
class BusinessException(BaseException):
    def __init__(self,code):
        #　错误码值
        self.code = code 
    
    def __str__(self):
        return 'ErrorCode:' + str(self.code)


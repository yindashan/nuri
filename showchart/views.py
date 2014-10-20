#!usr/bin/env python
# -*- coding:utf-8 -*-
#django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

# standard library

#our own code
from shownode.models import Chart, ShowChart
from redissync.models import ip2host
from monitorpoint.models import MonitorPoint
from appitem.models import AppService
from appitem.models import managable_app
from utils.utils import filterIP,ip_cmp


# 获取chart 编号
@login_required
def get_chart_id(request):
    if request.GET:
        app_id = int(request.GET.get('app_id'))
        app = AppService.objects.get(id=app_id)
        ip = request.GET.get('host')
        host = ip2host(ip)# IP地址转换为主机ID  
        monitor_id = request.GET.get('monitor_id')# 监控项ID
        
        res = MonitorPoint.objects.filter(appname=app.app_name, host=host, mid=monitor_id, is_valid=1)# 监控点信息
        chart = Chart()
        chart.point_id = res[0].id
        chart.node_id =  -1
        chart.save()
        
        return HttpResponse(chart.id)
    return  HttpResponseBadRequest("错误请求")

# 快速展示(以应用项为维度)
@login_required  
def quickshow(request):
    if request.method == 'GET':
        auth_set = request.session["authority_set"]
        # 可以对其监控项进行读操作的应用
        app_list = managable_app(auth_set)
        
        return render_to_response('showchart/quickshow.html', {'app_list':app_list}) 
    return  HttpResponseBadRequest("错误请求")

# 快速展示(以主机为维度)
@login_required  
def hostquickshow(request):
    if request.method == 'GET':
        auth_set = request.session["authority_set"]
        # 可以对其监控项进行读操作的应用
        app_list = managable_app(auth_set)
                
        ip_temp = [] 
        ip_list = []
        for b in app_list:
            ip_temp = (b.ip_list).split(',')
            ip_list  +=  ip_temp
        ip_list = filterIP(ip_list)
        
        return render_to_response('showchart/hostquickshow.html', {'ip_list':ip_list}) 
    return  HttpResponseBadRequest("错误请求")

# 展示App,host上的所有监控项图表
@login_required  
def simplechart(request):
    if request.method == 'GET':
        app_id = int(request.GET.get('app_id'))
        appname = AppService.objects.get(id=app_id).app_name
        host_ip = request.GET.get('host')
        host_id = settings.REDIS_DB.hget('ip_host', host_ip)
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        point_list = MonitorPoint.objects.filter(is_valid=1, appname=appname, host=host_id)
        res_list = []
        for point in point_list:
            res_list.append(ShowChart(Chart(point_id=point.id), start_time, end_time))
        return render_to_response('showchart/charts.html', {'chart_list':res_list} ) 
    return  HttpResponseBadRequest("错误请求")

    
    
    
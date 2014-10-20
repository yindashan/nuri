#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required


import json
import time
from datetime import datetime
from redissync.models import sync_app_mitem
from monitoritem.models import MonitorItem 
from monitorpoint.models import PointData, MonitorPoint
from monitorpoint.logic import sync_monitor_point
from monitoritem.models import generate_threshold, parse_threshold
from appitem.models import AppService, managable_app_id
from utils.constants import monitor_item_dict
from log.models import Log
from authority.decorators import permission_required

@login_required
def index(request):
    app_id_list = managable_app_id(request.session["authority_set"])
    apps = AppService.objects.filter(id__in = app_id_list).order_by('app_name')
    return render_to_response('monitoritem/index.html', {'app_list':apps})

#删除记录
#@login_required
@permission_required('monitor_manage')
def delete(request, item_id):
    item  = None
    try:
        item = MonitorItem.objects.get(id=int(item_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'监控项不存在!'}), mimetype='application/json')
    item.delete()
    
    #　根据监控项变化情况，同步监控点
    sync_monitor_point(item.app)
    
    # 同步应用的监控规则
    sync_app_mitem(item.app)
    
    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 4
    log.relate_id = item.id
    log.content="execute delete monitoritem " + item.app.app_name + " " + item.desc + " success!"
    log.level = 1
    log.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/monitoritem/index", "message":u'删除成功'}), mimetype='application/json')

#@login_required
@permission_required('monitor_manage')
def add(request):
    app_list = AppService.objects.all();
    if request.POST:
        mitem = MonitorItem()
        
        mitem.monitor_type = request.POST.get('monitor_type')
        var_name = request.POST.get('var_name')
        # 去除空格
        mitem.var_name = var_name.strip()
        mitem.formula = request.POST.get('formula')
        
        warning_type = request.POST.get('warning_type')
        w = request.POST.get('w')
        w1 = request.POST.get('w1')
        w2 = request.POST.get('w2')
        mitem.warning_threshold = generate_threshold(warning_type,w,w1,w2)
            
        critical_type = request.POST.get('critical_type')
        c = request.POST.get('c')
        c1 = request.POST.get('c1')
        c2 = request.POST.get('c2')
        mitem.critical_threshold = generate_threshold(critical_type,c,c1,c2)
        
        mitem.desc = request.POST.get('desc')
        mitem.app_id = request.POST.get('app_id')
        
        mitem.save()

        #　根据监控项变化情况，同步监控点
        sync_monitor_point(mitem.app)
        
        # 同步应用的监控规则
        sync_app_mitem(mitem.app)
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 4
        log.relate_id = mitem.id
        log.content="execute add monitoritem " + mitem.app.app_name + " " + mitem.desc + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/monitoritem/index", "message":u'添加成功'}), mimetype='application/json')        
    return render_to_response('monitoritem/add.html',{'app_list':app_list}) 

#@login_required
@permission_required('monitor_manage')
def edit(request, item_id):
    app_list = AppService.objects.all()
    item = MonitorItem.objects.get(id=int(item_id))
    warning_tuple = parse_threshold(item.warning_threshold)
    critical_tuple = parse_threshold(item.critical_threshold)
    
    if request.POST:
        
        item.monitor_type = request.POST.get('monitor_type')
        item.var_name = request.POST.get('var_name')
        # 去除空格
        item.var_name = item.var_name.strip()
        item.formula = request.POST.get('formula')

        warning_type = request.POST.get('warning_type')
        w = request.POST.get('w')
        w1 = request.POST.get('w1')
        w2 = request.POST.get('w2')
        item.warning_threshold = generate_threshold(warning_type,w,w1,w2)
           
        critical_type = request.POST.get('critical_type')
        c = request.POST.get('c')
        c1 = request.POST.get('c1')
        c2 = request.POST.get('c2')
        item.critical_threshold = generate_threshold(critical_type,c,c1,c2)

        item.desc = request.POST.get('desc')
        item.save()
        
        # 同步应用的监控规则
        sync_app_mitem(item.app)
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 4
        log.relate_id = item.id
        log.content="execute edit monitoritem " + item.app.app_name + " " + item.desc + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/monitoritem/index", "message":u'编辑成功'}), mimetype='application/json')    
    return render_to_response('monitoritem/edit.html',{'app_list':app_list,'item':item,'warning_tuple':warning_tuple,'critical_tuple':critical_tuple})
    
#@login_required
@permission_required('monitor_manage')
def search(request):
    if request.POST:
        app_id = request.POST.get("app_id")
        query = request.POST.get("query")
        
        app_id_list = managable_app_id(request.session["authority_set"])
        items = MonitorItem.objects.filter(app_id__in=app_id_list).order_by('-id')#app_id__in=app_id_list表示app_id列表在app_id_list
        
        if app_id:
            app_id = int(app_id)
            items = items.filter(app_id=app_id)
            
        if query:
            items = items.filter(desc__icontains = query)
        
        paginator = Paginator(items, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
            
        return render_to_response('monitoritem/searchback.html', {'monitoritems':pager, 'monitor_item_dict':monitor_item_dict})
    else:
        return  HttpResponseBadRequest("错误请求")

# 自动计算step
# step_list    -- 步长列表 类型:list
# margin    --时间区间 单位:秒
def auto_step(step_list, margin):
    margin = margin / 60
    for step in step_list:
        if margin/step < 1000:
            return step
            
    return step_list[len(step_list) - 1]
    
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    
# 获取监控点数据
@login_required
def fetch_data(request):
    if request.method == 'GET':
        # 1. 处理参数
        point_id = int(request.GET.get('point_id'))
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        # 2. 自动确定步长
        mp = MonitorPoint.objects.get(id=point_id)
        app = AppService.objects.get(app_name=mp.appname)
        step_list = app.step_list.split(',')
        step_list = [ int(step) for step in step_list ]
        
        # 类型:time
        start_time = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        
        margin = total_seconds(end_time - start_time)
        step = auto_step(step_list, margin)
        point_list = PointData.objects.filter(point_id=point_id, step=step, time__gte=start, time__lte=end)
        res_list = []
        for point in point_list:
            item = {}
            item['time'] = time.mktime(point.time.timetuple())
            item['value'] = point.value
            res_list.append(item)
        
        return HttpResponse(content=json.dumps(res_list))
    return  HttpResponseBadRequest("错误请求")
    
    
    
    

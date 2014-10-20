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
from redissync.models import update_timestamp_by_nocid
from redissync.models import maintain_noc_ip_map
from monitorpoint.models import PointData, MonitorPoint
from appitem.models import AppService
from nocip.models import NOCIP
from utils.constants import noc_info_dict
from log.models import Log

@login_required
def index(request):
    return render_to_response('nocip/index.html', {'noc_info_dict':noc_info_dict})


#删除记录
@login_required
def delete(request, nocip_id):
    item  = None
    try:
        item = NOCIP.objects.get(id=int(nocip_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'当前机房IP对应信息不存在!'}), mimetype='application/json')
    item.delete()
    
    # 在redis中删除指定机房下指定IP
    maintain_noc_ip_map(item.nocid)
    
    # 更新当前机房下所有应用对应的时间戳
    update_timestamp_by_nocid(item.nocid)
    
    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 0
    log.relate_id = item.id
    log.content="execute delete nocip " + item.nocid + " " + item.ip + " success!"
    log.level = 1
    log.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/nocip/index", "message":u'删除成功'}), mimetype='application/json')


@login_required
def add(request):
    if request.POST:
        nocid = request.POST.get('nocid', None)
        ip_list = request.POST.get('ip_list', None)
        ip_list = ip_list.split(',')
        for ip in ip_list:
            # 判断noc+ip是否重复
            nocips = NOCIP.objects.filter(nocid__iexact=nocid, ip__iexact=ip)
            if nocips:
                continue
                #return HttpResponse(simplejson.dumps({"statusCode":400, "url": "/nocip/index", "message":u'当前机房IP对应信息已经存在不能添加'}), mimetype='application/json')   
            
            nocip = NOCIP(nocid=nocid, ip=ip)
            nocip.save()
        
        # 在redis中添加指定机房下ip列表
        maintain_noc_ip_map(nocid)
        
        # 更新当前机房下所有应用对应的时间戳
        update_timestamp_by_nocid(nocid)

        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/nocip/index", "message":u'添加成功'}), mimetype='application/json')        
    return render_to_response('nocip/add.html',{'noc_info_dict':noc_info_dict}) 


@login_required
def edit(request, nocip_id):
    nocip = NOCIP.objects.get(id=int(nocip_id))
    if request.POST:
        nocid = request.POST.get('nocid', None)
        ip = request.POST.get('ip', None)
        # 判断nocid+ip是否重复
        nocips = NOCIP.objects.filter(nocid__iexact=nocid, ip__iexact=ip).exclude(id=int(nocip_id))
        if nocips:
            return HttpResponse(simplejson.dumps({"statusCode":400, "url": "/nocip/index", "message":u'当前机房IP对应信息已经存在不能修改'}), mimetype='application/json')   
        
        nocip.nocid = nocid
        nocip.ip = ip
        nocip.save()
        
        # 更新机房IP对应信息
        maintain_noc_ip_map(nocid)
        
        # 更新当前机房下所有应用对应的时间戳
        update_timestamp_by_nocid(nocid)

        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 0
        log.relate_id = nocip.id
        log.content="execute edit nocip " + nocip.nocid + " " + nocip.ip + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/nocip/index", "message":u'编辑成功'}), mimetype='application/json')    
    return render_to_response('nocip/edit.html',{'nocip':nocip, 'noc_info_dict':noc_info_dict})
    
    
@login_required
def search(request):
    if request.POST:
        nocid = request.POST.get("nocid")
        ip = request.POST.get("ip")
        
        nocips = NOCIP.objects.all().order_by('-id')
        
        if nocid:
            nocips = nocips.filter(nocid__icontains=nocid)
        if ip:
            nocips = nocips.filter(ip__icontains = ip)
            
        paginator = Paginator(nocips, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
            
        return render_to_response('nocip/searchback.html', {'nocips':pager, 'noc_info_dict':noc_info_dict})
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
    
    
    
    

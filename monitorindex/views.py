#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

# stdandard library
import datetime

# 导入在forms.py 中定义的所有表单类。
from appitem.models import AppService
from monitoritem.models import MonitorItem
from log.models import Log
from authority.decorators import permission_required
from redissync.models import host2ip
from monitorindex.models import MonitorIndexData, MonitorIndexItem, get_monitor_index_dict, get_host_ip_list
from utils.constants import valid_type_dict, calc_method_dict

# 显示监控指数列表
@login_required
def index(request):
    monitorindex_list = MonitorIndexItem.objects.all().order_by("-id")
    
    paginator = Paginator(monitorindex_list, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
    
    return render_to_response('monitorindex/index.html',{'monitor_index_list':pager, 
                                                         'valid_type_dict':valid_type_dict,
                                                         'auth_set':request.session["authority_set"],
                                                         'calc_method_dict':calc_method_dict})

# 添加监控指数所需的监控项和计算方法等
@permission_required('monitor_index_operate')
def add(request):
    try:
        app_list = AppService.objects.filter(app_name="HOST_STATUS")
        host_status_id = app_list[0].id
        monitor_list = MonitorItem.objects.filter(app_id=host_status_id)
    except:
        app_list = []
        monitor_list = []
    
    if request.POST:
        monitor_index_item = MonitorIndexItem()
        
        monitor_index_item.desc = request.POST.get('desc')
        monitor_index_item.app_id = request.POST.get('app_id')
        monitor_index_item.monitor_id = request.POST.get('monitor_id')
        monitor_index_item.calc_method = request.POST.get('calc_method')
        if request.POST.get('ceiling') == '0':
            monitor_index_item.ceiling = request.POST.get('ceiling_number')
        else:
            monitor_index_item.ceiling = -1
        monitor_index_item.is_valid = request.POST.get('is_valid')
        
        monitor_index_item.save()
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 6
        log.relate_id = monitor_index_item.id
        log.content="execute add monitorindex " + monitor_index_item.app.app_name + " " + monitor_index_item.desc + " success!"
        log.level = 1
        log.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/monitorindex/index", "message":u'添加成功'}), mimetype='application/json')        
    return render_to_response('monitorindex/add.html',{'app_list':app_list, 'monitor_list':monitor_list}) 

# 编辑监控指数
@permission_required('monitor_index_operate')
def edit(request, item_id):
    try:
        app_list = AppService.objects.filter(app_name="HOST_STATUS")
        host_status_id = app_list[0].id
        monitor_list = MonitorItem.objects.filter(app_id=host_status_id)
    except:
        app_list = []
        monitor_list = []
    item = MonitorIndexItem.objects.get(id=int(item_id))
    
    if request.POST:
        item.desc = request.POST.get('desc')
        item.calc_method = request.POST.get('calc_method')
        if request.POST.get('ceiling') == '0':
            item.ceiling = request.POST.get('ceiling_number')
        else:
            item.ceiling = -1
        item.is_valid = request.POST.get('is_valid')
        item.save()
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 6
        log.relate_id = item.id
        log.content="execute edit monitorindex " + item.app.app_name + " " + item.desc + " success!"
        log.level = 1
        log.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/monitorindex/index", "message":u'编辑成功'}), mimetype='application/json')    
    return render_to_response('monitorindex/edit.html',{'app_list':app_list, 'monitor_list':monitor_list, 'item':item})

# 删除监控指数
@permission_required('monitor_index_operate')
def delete(request, item_id):
    item  = None
    try:
        item = MonitorIndexItem.objects.get(id=int(item_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'监控指数不存在!'}), mimetype='application/json')
    item.delete()

    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 6
    log.relate_id = item.id
    log.content="execute delete monitorindex " + item.app.app_name + " " + item.desc + " success!"
    log.level = 1
    log.save()
    
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/monitorindex/index", "message":u'删除成功'}), mimetype='application/json')


# 查看每日监控指数情况（各分项&总分值）
@login_required
def watch(request):
    # 主机列表（host_ip）
    try:
        app_service = AppService.objects.get(app_name="HOST_STATUS")
        ip_list = (app_service.ip_list).split(',')
    except:
        ip_list = []
    
    monitor_index_dict = get_monitor_index_dict()
    return render_to_response('monitorindex/watch.html', {'host_list':ip_list, 'monitor_index_dict': monitor_index_dict}) 

# 搜索显示监控健康指数
#@login_required
@permission_required('host_health')
def search(request):
    if request.method == 'POST':
        
        host_ip = request.POST.get('host')
        if host_ip != 'all_host':
            host_id = settings.REDIS_DB.hget('ip_host', host_ip)
        
        date = request.POST.get('date')
        # 如果无法取得日期，则默认为昨天
        if date == '':
            date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")

        # 取得排序信息        
        sort_item = request.POST.get('sort_item')  # 排序用的监控指数，默认为0:分数
        sort_method = request.POST.get('sort_method')  # 排序方式，desc:由高到低/asc:倒序，默认为desc
        sort_str = 'value' if sort_method == 'asc' else '-value'
         
        monitor_index_dict = get_monitor_index_dict()
        
        # 取得搜索日期的监控指数数据
        index_data_of_this_day = MonitorIndexData.objects.filter(monitor_date=date)
        
        # 按指定方法排序
        index_data_for_order = index_data_of_this_day.filter(key=sort_item)
        if host_ip != 'all_host':
            index_data_for_order = index_data_for_order.filter(host=host_id)
        index_data_for_order = index_data_for_order.order_by(sort_str)

        # 取得所有主机监控情况列表，格式为[{'host':主机ID, 'host_ip':主机IP, 'score':健康指数, 'index'：各监控指数（为字典）}, {}...]
        score_list = []
        for each in index_data_for_order:
            score_list.append({'host':each.host, 'index': {}})
        
        # 分页
        paginator = Paginator(score_list, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
            
        host_list = get_host_ip_list(pager)
        
        for i, line in enumerate(pager):
            each_index_data = index_data_of_this_day.filter(host=line['host'])
            index_data_dict = {}
            for e in each_index_data:
                index_data_dict[e.key] = e.value
            # 写入host_ip和健康指数得分
            line['host_ip'] = host_list[i]
            line['score'] = index_data_dict[0]
            # 写入各指数值
            index_data_dict.pop(0)
            for k, v in index_data_dict.items():
                line['index'][k] = v
            # 遍历监控指数字典，如果当前主机该日有的监控指数没有，则赋为None
            for k, v in monitor_index_dict.items():
                if not line['index'].has_key(k):
                    line['index'][k] = None
        
        return render_to_response('monitorindex/searchback.html', {'score_list': pager, 
                                                                   'monitor_index_dict': monitor_index_dict,
                                                                   'date': date,} ) 
    return  HttpResponseBadRequest("错误请求")


# 监控指数详细信息
#@login_required
@permission_required('host_health')
def detail(request, host_id, date):
    monitor_index_dict = get_monitor_index_dict()
    
    monitor_index_data = MonitorIndexData.objects.filter(monitor_date=date, host=host_id)
    
    score_list = {'host':host_id, 'host_ip':host2ip(host_id), 'index': {}}
    score_list['score'] = monitor_index_data.get(key=0).value
    
    for each in monitor_index_data:
        each_index_data =  monitor_index_data.filter(key__gt=0)
        for e in each_index_data:
            score_list['index'][monitor_index_dict[e.key]] = e.value
    
    return render_to_response('monitorindex/detail.html', {'score_list': score_list} ) 


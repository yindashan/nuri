#usr/bin/env python
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
import json


# 导入在forms.py 中定义的所有表单类。
from appitem.models import AppService, managable_app_id
from appitem.models import create_perm_record, gen_step_info, AppRepr
from log.models import Log
from utils.constants import alarm_type_dict
from monitoritem.models import monitorItem2Temp
from monitorpoint.logic import sync_monitor_point
from utils.jsonhelp import complexObj2json
from utils.utils import filterIP
from authority.decorators import permission_required
from redissync.models import get_host, sync_app_info
from redissync.models import update_app_timestamp, sync_app_change
from redissync.models import add_noc_app_map, update_noc_app_map
from monitoritem.models import MonitorItem, app_mitem
from utils.constants import noc_info_dict, app_type_dict, notify_dict
from utils.constants import retry_dict, check_dict, monitor_item_dict
from appitem.logic import save_pc_rel, remove_app
from redissync.models import sync_app_mitem


##显示应用列表
@login_required
def index(request): 
    app_id_list = managable_app_id(request.session["authority_set"])
    apps = AppService.objects.filter(id__in = app_id_list).order_by('app_name')
    return render_to_response('appitem/index.html', {'app_list':apps,'auth_set':request.session["authority_set"],\
                                                     'alarm_type_dict':alarm_type_dict,'app_type_dict':app_type_dict})

@permission_required('appitem_operate')
def add(request, pid):
    if request.method == "GET":
        return render_to_response('appitem/add.html', {'noc_info_dict':noc_info_dict, 'parent_id':pid})
    else:
        return  HttpResponseBadRequest("错误请求")

@permission_required('appitem_operate')
def add_save(request):
    if request.method == 'POST':
        app_name = request.POST.get('app_name')
        
        # 验证重复应用名
        app = AppService.objects.filter(app_name__iexact=app_name)
        if app:
            return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'应用服务记录已经存在不能添加'}), mimetype='application/json')

        app = AppService()
        app.app_name = app_name.strip()
        app.desc = request.POST.get('desc')
        app.ip_list = request.POST.get('ip_list')
        app.check_interval = int(request.POST.get('check_interval'))
        app.max_check_attempts = int(request.POST.get('max_check_attempts'))
        # 过滤IP列表防止出现重复的IP地址        
        ip_list = filterIP(app.ip_list.split(','))
        host_list = get_host(ip_list)
        app.ip_list = ','.join(ip_list)
        app.host_list = ','.join(host_list)
         
        app.email_list = request.POST.get('email_list')#报警邮件收件人列表
        app.mobile_list = request.POST.get('mobile_list')#报警短信收件人
        
        app.is_alarm = request.POST.get('is_alarm')#是否报警

        app.step_list = gen_step_info(app)
        # 添加当前应用机房分布情况
        noc_list = request.POST.getlist('noc_list', None)
        app.noc_list = ','.join(noc_list)
        
        # 通知间隔    
        app.notify_interval = int(request.POST.get('notify_interval'))
        
        # 应用类型
        app.type = int(request.POST.get('app_type'))
        
        app.save()
        
        #  保存应用的父子关系
        parent_id = request.POST.get('parent_id')
        save_pc_rel(app, int(parent_id))
        
        # 创建对应的权限记录 此应用监控项的读和操作权限
        create_perm_record(app.app_name)
        
        #　同步应用配置
        sync_app_info(app)
        
        # 添加noc_app_map中该应用相关的信息
        add_noc_app_map(app)
        
        # 同步应用的监控规则
        sync_app_mitem(app)
        
        #　同步监控点
        sync_monitor_point(app)
        
        # 更新当前应用对应的时间戳，如果不存在，则生成
        update_app_timestamp(app)
        
        # 同步应用检查计划　
        sync_app_change(app)
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 3
        log.relate_id = app.id
        log.content="execute add appitem " + app.app_name + " success!"
        log.level = 1
        log.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/appitem/index", "message":u'添加成功'}), mimetype='application/json')
    
    return  HttpResponseBadRequest("错误请求")
    
# 删除记录
@permission_required('appitem_operate')
def delete(request, app_id):
    app = AppService.objects.get(id=int(app_id))
    try:
        app = AppService.objects.get(id=int(app_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'应用项不存在!'}), mimetype='application/json')
    
    remove_app(app)
    
    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 3
    log.relate_id = app.id
    log.content="execute delete appitem " + app.app_name + " success!"
    log.level = 1
    log.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/appitem/index", "message":u'删除成功'}), mimetype='application/json')

@login_required
def edit(request, app_id):
    app = None
    try:
        app = AppService.objects.get(id=int(app_id))
        noc_list_tmp = app.noc_list.split(',')
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'应用项不存在!'}), mimetype='application/json')
    if request.method == 'POST':
        app.desc = request.POST.get('desc')
        app.ip_list = request.POST.get('ip_list')
        app.check_interval = int(request.POST.get('check_interval'))
        app.max_check_attempts = int(request.POST.get('max_check_attempts'))
        
        # 过滤IP列表防止出现重复的IP地址        
        ip_list = filterIP(app.ip_list.split(','))
        host_list = get_host(ip_list)
        app.ip_list = ','.join(ip_list)
        app.host_list = ','.join(host_list)
        app.email_list = request.POST.get('email_list', None)
        app.mobile_list = request.POST.get('mobile_list', None)
        
        app.is_alarm = request.POST.get('is_alarm')#是否报警
            
        app.step_list = gen_step_info(app)
        
        # 添加当前应用机房分布情况
        noc_list = request.POST.getlist('noc_list', None)
        app.noc_list = ','.join(noc_list)
        
        # 通知间隔    
        app.notify_interval = int(request.POST.get('notify_interval'))
        
        # 应用类型
        app.type = int(request.POST.get('app_type'))
        
        app.save()
        
        # 将应用的配置信息写入redis
        sync_app_info(app)
        
        # 更新noc_app_map中该应用相关的信息
        update_noc_app_map(app, noc_list_tmp)
        
        # 根据监控项变化情况，同步监控点
        sync_monitor_point(app)
        
        # 更新当前应用对应的时间戳
        update_app_timestamp(app)
        
        # 同步应用检查计划　
        sync_app_change(app)
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 3
        log.relate_id = app.id
        log.content = "execute edit appitem " + app.app_name + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/appitem/index", "message":u'编辑成功'}), mimetype='application/json')  
    return render_to_response('appitem/edit.html', {'app': app, 'noc_list_tmp':noc_list_tmp, \
        'noc_info_dict':noc_info_dict, 'app_type_dict':app_type_dict, 'notify_dict':notify_dict,
        'retry_dict':retry_dict, 'check_dict':check_dict,'alarm_type_dict':alarm_type_dict})

# 供页面ajax请求使用
@login_required
def getappinfo(request):
    if request.method == 'POST':
        app_id = int(request.POST.get("app_id"))
        app = AppService.objects.get(id=app_id)
        host_list = app.ip_list.split(',')
        monitor_item_list = MonitorItem.objects.filter(app_id=app_id)
        monitor_list = monitorItem2Temp(monitor_item_list)
        dd = {}
        dd["host_list"] = host_list
        dd["monitor_list"] = complexObj2json(monitor_list)
        return HttpResponse(json.dumps(dd))
    else:
        return  HttpResponseBadRequest("错误请求")
    
# 供页面ajax请求使用
@login_required
def gethostinfo(request):
    if request.method == 'POST':
        ip = request.POST.get("host")
        app_list = AppService.objects.filter(ip_list__icontains=ip)
        app_name_list = []
        for i in app_list:
            app_name_list.append({"app_name":i.app_name,"app_id":i.id})

        return HttpResponse(json.dumps(app_name_list))
    else:
        return  HttpResponseBadRequest("错误请求")


@login_required
def search(request):
    if request.method == 'POST':
        app_id = request.POST.get("app_id")
        is_alarm = request.POST.get("is_alarm")
        ntype = request.POST.get("type")
        
        app_id_list = managable_app_id(request.session["authority_set"])
        items = AppService.objects.filter(id__in = app_id_list).order_by('app_name')
        print app_id
	print len(app_id)
        if app_id:
	    print '-----------2-------'
            app_id = int(app_id)
            items = items.filter(id=app_id)

        if  is_alarm:
            items = items.filter(is_alarm = is_alarm)
        if  ntype:
            items = items.filter(type = ntype)      
            
        paginator = Paginator(items, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
            
        res_list = []
        for app in pager:
            res_list.append(AppRepr(app))
        pager.object_list = res_list
        
        return render_to_response('appitem/searchback.html', {'app_list':pager, 'alarm_type_dict':alarm_type_dict,\
                                                              'app_type_dict':app_type_dict,'auth_set':request.session["authority_set"]})
    else:
        return  HttpResponseBadRequest("错误请求")
        

@login_required
def mitem(request, app_id):
    app = AppService.objects.get(id=app_id)
    item_list = app_mitem(app)
    return render_to_response('appitem/mitem.html',{'curr_app':app.app_name,
        'monitoritems':item_list, 'monitor_item_dict':monitor_item_dict})
        
@login_required        
def active(request, appname, mid):
    mitem = MonitorItem.objects.get(id=mid)
    new_item = mitem.clone()
    app = AppService.objects.get(app_name=appname)
    new_item.app = app
    new_item.save()
    
    # 根据监控项变化情况，同步监控点
    sync_monitor_point(app)
    
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/appitem/mitem/%d/" % (app.id), "message":u'激活成功'}),
        mimetype='application/json')
    
    
    
    
    
    
    
    
    

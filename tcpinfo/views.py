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

from redissync.models import sync_app_mitem
from redissync.models import update_app_timestamp
from redissync.models import maintain_tcp_port_configuration
from monitoritem.models import MonitorItem
from monitorpoint.logic import sync_monitor_point
from monitoritem.models import generate_threshold
from appitem.models import AppService, managable_app_id
from tcpinfo.models import TCPInfo
from log.models import Log

@login_required
def index(request):
    app_id_list = managable_app_id(request.session["authority_set"])
    apps = AppService.objects.filter(id__in = app_id_list, type = 3).order_by('app_name')
    return render_to_response('tcpinfo/index.html', {'app_list':apps})

# 删除记录
@login_required
def delete(request, tcp_id):
    item  = None
    try:
        item = TCPInfo.objects.get(id=int(tcp_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'当前TCP服务不存在!'}), mimetype='application/json')
    item.delete()
    
    # 维护redis中当前应用的配置信息
    maintain_tcp_port_configuration(item.app)
    
    # 维护监控项信息
    maintain_monitoritem_delete(item)
    
    # 更新当前应用对应的时间戳
    update_app_timestamp(item.app)
    
    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 0
    log.relate_id = item.id
    log.content="execute delete tcpinfo " + item.app.app_name + " " + item.port + " success!"
    log.level = 1
    log.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/tcpinfo/index", "message":u'删除成功'}), mimetype='application/json')


@login_required
def add(request):
    app_list = AppService.objects.filter(type = 3)
    if request.POST:
        port_list = request.POST.get('port_list', None)
        responsetime = request.POST.get('responsetime', None)
        app_id = request.POST.get('app_id', 1)
        
        for port in port_list.split(','):
            # 判断tcp是否重复
            tcpinfos = TCPInfo.objects.filter(app_id=app_id, port=port)
            if tcpinfos:
                continue
            tcpinfo = TCPInfo(port=port, responsetime=responsetime, app_id=app_id)
            tcpinfo.save()
            
            # 维护监控项
            maintain_monitoritem_add_or_update(tcpinfo)
        
        # 维护redis中当前应用的配置信息
        maintain_tcp_port_configuration(tcpinfo.app)
        
        # 更新当前应用对应的时间戳
        update_app_timestamp(tcpinfo.app)
        

        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/tcpinfo/index", "message":u'添加成功'}), mimetype='application/json')        
    return render_to_response('tcpinfo/add.html',{'app_list':app_list})


@login_required
def edit(request, tcp_id):
    app_list = AppService.objects.filter(type = 3)
    tcpinfo = TCPInfo.objects.get(id=int(tcp_id))
    
    if request.POST:
        tcpinfo.responsetime = request.POST.get('responsetime', None)
        
        tcpinfo.save()
        
        # 维护redis中当前应用的配置信息
        maintain_tcp_port_configuration(tcpinfo.app)
        
        # 维护监控项
        maintain_monitoritem_add_or_update(tcpinfo)
        
        # 更新当前应用对应的时间戳
        update_app_timestamp(tcpinfo.app)

        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 0
        log.relate_id = tcpinfo.id
        log.content="execute edit tcpinfo " + tcpinfo.app.app_name + " " + tcpinfo.port + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/tcpinfo/index", "message":u'编辑成功'}), mimetype='application/json')    
    return render_to_response('tcpinfo/edit.html',{'app_list':app_list, 'tcpinfo':tcpinfo})
    
    
@login_required
def search(request):
    if request.POST:
        app_id = request.POST.get("app_id")
        query = request.POST.get("query")
        
        app_id_list = managable_app_id(request.session["authority_set"])

        tcpinfos = TCPInfo.objects.filter(app_id__in=app_id_list).order_by('-id')
        
        if app_id:
            app_id = int(app_id)
            tcpinfos = tcpinfos.filter(app_id=app_id)
        if query:
            tcpinfos = tcpinfos.filter(port__iexact = query)
            
        paginator = Paginator(tcpinfos, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
            
        return render_to_response('tcpinfo/searchback.html', {'tcpinfos':pager})
    else:
        return  HttpResponseBadRequest("错误请求")

def monitoritem_add(prefix, tcpinfo, var_name):
    """
    维护监控项：根据变量名称添加监控项信息
    """
    mitem = MonitorItem()
    mitem.monitor_type = 1 # 表示监控项类型：单个变量
    mitem.var_name = var_name
    mitem.formula = ''
    
    # 判断当前应用下是否已经存在此监控项，如果存在，则直接跳出,判断依据：同一个应用下变量名称是唯一的
    monitoritems = MonitorItem.objects.filter(var_name__iexact=var_name, app_id=tcpinfo.app.id)
    if monitoritems:
        return
    
    warning_type = '2' # 表示x<w
    mitem.warning_threshold = generate_threshold(warning_type, '1', '', '')
    
    critical_type = '2' # 表示x<c
    mitem.critical_threshold = generate_threshold(critical_type, '1', '', '')
    
    
    mitem.desc = prefix + str(tcpinfo.port)
    mitem.app_id = tcpinfo.app.id
    
    mitem.save()

    #　根据监控项变化情况，同步监控点
    sync_monitor_point(tcpinfo.app)
    
    # 同步应用的监控规则
    sync_app_mitem(tcpinfo.app)




def monitoritem_add_responsetime(prefix, tcpinfo, var_name):
    """
    维护监控项：根据变量名称添加监控项信息
    """
    mitem = MonitorItem()
    mitem.monitor_type = 1 # 表示监控项类型：单个变量
    mitem.var_name = var_name
    mitem.formula = ''
    
    # 判断当前应用下是否已经存在此监控项，如果存在，则直接跳出,判断依据：同一个应用下变量名称是唯一的
    monitoritems = MonitorItem.objects.filter(var_name__iexact=var_name, app_id=tcpinfo.app.id)
    if monitoritems:
        return
    
    warning_type = '1' # 表示x>w
    mitem.warning_threshold = generate_threshold(warning_type, tcpinfo.responsetime, '', '')
    
    critical_type = '1' # 表示x>c
    mitem.critical_threshold = generate_threshold(critical_type, tcpinfo.responsetime, '', '')
    
    
    mitem.desc = prefix + str(tcpinfo.port)
    mitem.app_id = tcpinfo.app.id
    
    mitem.save()

    #　根据监控项变化情况，同步监控点
    sync_monitor_point(tcpinfo.app)
    
    # 同步应用的监控规则
    sync_app_mitem(tcpinfo.app)


def monitoritem_delete(tcpinfo, var_name):
    """
    维护监控项：根据变量名称删除监控项信息
    """
    # 判断当前应用下是否存在此监控项，如果存在，则删除,如果不存在，则直接退出
    monitoritems = MonitorItem.objects.filter(var_name__iexact=var_name, app_id=tcpinfo.app.id)
    if monitoritems:
        monitoritems.delete()
    else:
        return
    
    #　根据监控项变化情况，同步监控点
    sync_monitor_point(tcpinfo.app)
    
    # 同步应用的监控规则
    sync_app_mitem(tcpinfo.app)
    
def maintain_monitoritem_add_or_update(tcpinfo):
    """
    维护监控项：更新或修改tcpinfo时触发此函数
    """
    # 添加TCP状态检查监控项
    status_prefix = u'端口存活性(0:DOWN,1:UP)：端口'
    status_var_name = 'tcp_' + str(tcpinfo.port) + '_status'
    monitoritem_add(status_prefix, tcpinfo, status_var_name)
    
    responsetime_prefix = u'响应时间检查(单位:毫秒)：端口'
    responsetime_var_name = 'tcp_' + str(tcpinfo.port) + '_responsetime'
    if tcpinfo.responsetime != None and tcpinfo.responsetime != '':
        monitoritem_add_responsetime(responsetime_prefix, tcpinfo, responsetime_var_name)
    else:
        monitoritem_delete(tcpinfo, responsetime_var_name)
        
    
    
def maintain_monitoritem_delete(tcpinfo):
    """
    维护监控项：删除tcpinfo时触发此函数
    """
    # 删除URL状态检查监控项
    status_var_name = 'tcp_' + str(tcpinfo.port) + '_status'
    monitoritem_delete(tcpinfo, status_var_name)
    
    # 删除URL响应时间监控项
    responsetime_var_name = 'tcp_' + str(tcpinfo.port) + '_responsetime'
    monitoritem_delete(tcpinfo, responsetime_var_name)

    
    
    
    

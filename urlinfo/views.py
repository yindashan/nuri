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

import urlparse

from redissync.models import get_host
from redissync.models import sync_app_info
from redissync.models import sync_app_mitem
from redissync.models import update_app_timestamp
from redissync.models import maintain_http_url_configuration
from monitoritem.models import MonitorItem
from monitorpoint.logic import sync_monitor_point
from monitoritem.models import generate_threshold
from appitem.models import AppService, managable_app_id
from urlinfo.models import URLInfo
from log.models import Log

from utils.utils import filterIP

@login_required
def index(request):
    app_id_list = managable_app_id(request.session["authority_set"])
    apps = AppService.objects.filter(id__in = app_id_list, type = 1).order_by('app_name')
    return render_to_response('urlinfo/index.html', {'app_list':apps})


#删除记录
@login_required
def delete(request, url_id):
    item  = None
    try:
        item = URLInfo.objects.get(id=int(url_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'当前URL不存在!'}), mimetype='application/json')
#    item.delete()
    item.is_deleted = 0
    item.save()
    
    # 维护redis中当前应用的配置信息
    maintain_http_url_configuration(item.app)
    
    # 维护监控项信息
    maintain_monitoritem_delete(item)
    
    # 更新当前应用对应的时间戳
    update_app_timestamp(item.app)
    
    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 0
    log.relate_id = item.id
    log.content="execute delete urlinfo " + item.app.app_name + " " + item.url + " success!"
    log.level = 1
    log.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/urlinfo/index", "message":u'删除成功'}), mimetype='application/json')


@login_required
def add(request):
    app_list = AppService.objects.filter(type = 1);
    if request.POST:
        url = request.POST.get('url', None)
        responsetime = request.POST.get('responsetime', None)
        type = request.POST.get('type', None)
        target = request.POST.get('target', None)
        value = request.POST.get('value', None)
        app_id = request.POST.get('app_id', 1)
        
        # 判断url是否重复
        urlinfos = URLInfo.objects.filter(url__iexact=url, is_deleted=1)
        if urlinfos:
            return HttpResponse(simplejson.dumps({"statusCode":400, "url": "/urlinfo/index", "message":u'当前URL已经存在不能添加'}), mimetype='application/json')   
        
        urlinfo = URLInfo(url=url, responsetime=responsetime, type=type, target=target, value=value, app_id=app_id)
        urlinfo.save()
        
        # 维护redis中当前应用的配置信息
        maintain_http_url_configuration(urlinfo.app)
        
        # 维护监控项
        maintain_monitoritem_add_or_update(urlinfo)
        
        # 更新当前应用对应的时间戳
        update_app_timestamp(urlinfo.app)
        

        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 0
        log.relate_id = urlinfo.id
        log.content="execute add urlinfo " + urlinfo.app.app_name + " " + urlinfo.url + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/urlinfo/index", "message":u'添加成功'}), mimetype='application/json')        
    return render_to_response('urlinfo/add.html',{'app_list':app_list}) 


@login_required
def edit(request, url_id):
    app_list = AppService.objects.filter(type = 1)
    urlinfo = URLInfo.objects.get(id=int(url_id))
    
    if request.POST:
        # 禁止修改url
#        url = request.POST.get('url', None)
#        urlinfos = URLInfo.objects.filter(url__iexact=url, is_deleted=1).exclude(id=int(url_id))
#        if urlinfos:
#            return HttpResponse(simplejson.dumps({"statusCode":400, "url": "/urlinfo/index", "message":u'当前URL已经存在不能修改'}), mimetype='application/json')   
#        
#        urlinfo.url = url
        urlinfo.responsetime = request.POST.get('responsetime', None)
        urlinfo.type = request.POST.get('type', None)
        urlinfo.target = request.POST.get('target', None)
        urlinfo.value = request.POST.get('value', None)
        
        urlinfo.save()
        
        # 维护redis中当前应用的配置信息
        maintain_http_url_configuration(urlinfo.app)
        
        # 维护监控项
        maintain_monitoritem_add_or_update(urlinfo)
        
        # 更新当前应用对应的时间戳
        update_app_timestamp(urlinfo.app)

        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 0
        log.relate_id = urlinfo.id
        log.content="execute edit urlinfo " + urlinfo.app.app_name + " " + urlinfo.url + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/urlinfo/index", "message":u'编辑成功'}), mimetype='application/json')    
    return render_to_response('urlinfo/edit.html',{'app_list':app_list, 'urlinfo':urlinfo})
    
    
@login_required
def search(request):
    if request.POST:
        app_id = request.POST.get("app_id")
        query = request.POST.get("query")
        
        app_id_list = managable_app_id(request.session["authority_set"])

        urlinfos = URLInfo.objects.filter(app_id__in=app_id_list, is_deleted=1).order_by('-id')
        
        if app_id:
            app_id = int(app_id)
            urlinfos = urlinfos.filter(app_id=app_id)
        if query:
            urlinfos = urlinfos.filter(url__icontains = query)
            
        paginator = Paginator(urlinfos, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
            
        return render_to_response('urlinfo/searchback.html', {'urlinfos':pager})
    else:
        return  HttpResponseBadRequest("错误请求")






def monitoritem_add(prefix, urlinfo, var_name):
    """
    维护监控项：根据变量名称添加监控项信息
    """
    mitem = MonitorItem()
    mitem.monitor_type = 1 # 表示监控项类型：单个变量
    mitem.var_name = var_name
    mitem.formula = ''
    
    # 判断当前应用下是否已经存在此监控项，如果存在，则直接跳出,判断依据：同一个应用下变量名称是唯一的
    monitoritems = MonitorItem.objects.filter(var_name__iexact=var_name, app_id=urlinfo.app.id)
    if monitoritems:
        return
    
    warning_type = '2' # 表示x<w
    w = '1'
    w1 = ''
    w2 = ''
    mitem.warning_threshold = generate_threshold(warning_type, w, w1, w2)
    
    critical_type = '2' # 表示x<c
    c = '1'
    c1 = ''
    c2 = ''
    mitem.critical_threshold = generate_threshold(critical_type, c, c1, c2)
    
    
    mitem.desc = prefix + urlinfo.url
    mitem.app_id = urlinfo.app.id
    
    mitem.save()

    #　根据监控项变化情况，同步监控点
    sync_monitor_point(urlinfo.app)
    
    # 同步应用的监控规则
    sync_app_mitem(urlinfo.app)



def monitoritem_add_responsetime(prefix, urlinfo, var_name):
    """
    维护监控项：根据变量名称添加监控项信息
    """
    mitem = MonitorItem()
    mitem.monitor_type = 1 # 表示监控项类型：单个变量
    mitem.var_name = var_name
    mitem.formula = ''
    
    # 判断当前应用下是否已经存在此监控项，如果存在，则直接跳出,判断依据：同一个应用下变量名称是唯一的
    monitoritems = MonitorItem.objects.filter(var_name__iexact=var_name, app_id=urlinfo.app.id)
    if monitoritems:
        return
    
    warning_type = '1' # 表示x>w
    w = urlinfo.responsetime
    w1 = ''
    w2 = ''
    mitem.warning_threshold = generate_threshold(warning_type, w, w1, w2)
    
    critical_type = '1' # 表示x>c
    c = urlinfo.responsetime
    c1 = ''
    c2 = ''
    mitem.critical_threshold = generate_threshold(critical_type, c, c1, c2)
    
    
    mitem.desc = prefix + urlinfo.url
    mitem.app_id = urlinfo.app.id
    
    mitem.save()

    #　根据监控项变化情况，同步监控点
    sync_monitor_point(urlinfo.app)
    
    # 同步应用的监控规则
    sync_app_mitem(urlinfo.app)


def monitoritem_delete(urlinfo, var_name):
    """
    维护监控项：根据变量名称删除监控项信息
    """
    # 判断当前应用下是否存在此监控项，如果存在，则删除,如果不存在，则直接退出
    monitoritems = MonitorItem.objects.filter(var_name__iexact=var_name, app_id=urlinfo.app.id)
    if monitoritems:
        monitoritems.delete()
    else:
        return
    
    #　根据监控项变化情况，同步监控点
    sync_monitor_point(urlinfo.app)
    
    # 同步应用的监控规则
    sync_app_mitem(urlinfo.app)
    
    
    
    
    
    
def maintain_monitoritem_add_or_update(urlinfo):
    """
    维护监控项：更新或修改urlinfo时触发此函数
    """
    # 添加URL状态检查监控项
    status_prefix = u'状态检查：'
    status_var_name = 'url_' + str(urlinfo.id) + '_status'
    monitoritem_add(status_prefix, urlinfo, status_var_name)
    
    responsetime_prefix = u'响应时间检查：'
    responsetime_var_name = 'url_' + str(urlinfo.id) + '_responsetime'
    if urlinfo.responsetime != None and urlinfo.responsetime != '':
        monitoritem_add_responsetime(responsetime_prefix, urlinfo, responsetime_var_name)
    else:
        monitoritem_delete(urlinfo, responsetime_var_name)
        
    content_prefix = u'返回内容检查：'
    content_var_name = 'url_' + str(urlinfo.id) + '_content'
    if urlinfo.type != None and urlinfo.type != '' and urlinfo.target != None and urlinfo.target != '' and urlinfo.value != None and urlinfo.value != '':
        monitoritem_add(content_prefix, urlinfo, content_var_name)
    else:
        monitoritem_delete(urlinfo, content_var_name)
    
    
def maintain_monitoritem_delete(urlinfo):
    """
    维护监控项：删除urlinfo时触发此函数
    """
    # 删除URL状态检查监控项
    status_var_name = 'url_' + str(urlinfo.id) + '_status'
    monitoritem_delete(urlinfo, status_var_name)
    
    # 删除URL响应时间监控项
    responsetime_var_name = 'url_' + str(urlinfo.id) + '_responsetime'
    monitoritem_delete(urlinfo, responsetime_var_name)
    
    # 删除URL返回内容监控项
    content_var_name = 'url_' + str(urlinfo.id) + '_content'
    monitoritem_delete(urlinfo, content_var_name)
    
    
    

def import_url(appname, server, url):
    """
    url导入函数
    """
    try:
        # 判断应用管理模块是否存在应用名为appname的应用
        apps = AppService.objects.filter(app_name__iexact=appname, type = 1)
        if not apps: # 不存在应用名为appname的应用，直接跳过
            return False
        else: # 存在应用名为appname的应用
            app = apps[0]
            
            # 判断当前应用下是否已经存在此url信息
            urlinfos = URLInfo.objects.filter(url__iexact=url, is_deleted=1)
            if urlinfos: # 已经存在，不用再添加url信息，直接添加此url的监控项
                urlinfo = urlinfos[0]
                # 维护监控项
                maintain_monitoritem_add_or_update(urlinfo)
            else: # 不存在，添加此url信息,且添加此url的监控项
                urlinfo = URLInfo(url=url, responsetime='', type='', target='', value='', app_id=app.id)
                urlinfo.save()
                
                # 维护redis中当前应用的配置信息
                maintain_http_url_configuration(urlinfo.app)
                
                # 维护监控项
                maintain_monitoritem_add_or_update(urlinfo)
                
                # 更新当前应用对应的时间戳
                update_app_timestamp(urlinfo.app)
            
            # 过滤IP列表防止出现重复的IP地址
            ip_list = filterIP(app.ip_list.split(','))
            # 判断当前应用下是否已经存在此server
            if server not in ip_list:
                ip_list.append(server)
            host_list = get_host(ip_list)
            app.ip_list = ','.join(ip_list)
            app.host_list = ','.join(host_list)
            app.save()
            
            # 将应用的配置信息写入redis
            sync_app_info(app)
            
            # 根据监控项变化情况，同步监控点
            sync_monitor_point(app)
            
            # 更新当前应用对应的时间戳
            update_app_timestamp(app)
            
            
    except Exception, e:
        print e
    
    return True
    
    

def parseLine(line):
    """
    解析原始文件中的单行数据
    """
    try:
        line_list = line.split('==')
        if len(line_list) != 2:
            return
        else:
            appname = line_list[0]
            url = line_list[1]
            host, path = urlparse.urlsplit(url)[1:3]
            if ':' in host:
                host, port = host.split(':', 1)
                try:
                    port = int(port)
                except ValueError:
                    pass
            else:
                port=80
            server = host
            url = url.replace(host, '{ip}').strip()
            # 导入url信息
            import_url(appname, server, url)
            
    except Exception, e:
        print e
    



@login_required
def upload(request):
    if request.POST:
        if request.FILES:
            try:
                ff = request.FILES['urlfile']
                lines = ff.readlines()
                ff.close()
                for line in lines:
                    line = line.strip()
                    if line != None and line != '' and not line.startswith('#'):
                        # 解析单行数据
                        parseLine(line)
            except Exception, e:
                print e
        return render_to_response('urlinfo/uploadsuccess.html')
        #return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/urlinfo/index", "message":u'导入成功'}), mimetype='application/json')
    return render_to_response('urlinfo/upload.html', {}, context_instance=RequestContext(request))

    
    



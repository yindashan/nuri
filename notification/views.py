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


from appitem.models import AppService, managable_app
from notification.models import Notification, HostEvent
from redissync.models import ip2host, get_all_ip

@login_required
def index(request):
    app_list = managable_app(request.session["authority_set"])
    return render_to_response('notification/index.html', {'app_list':app_list})
    
@login_required
def search(request):
    if request.method =='POST':
        app_id = request.POST.get("app_id")
        host_ip = request.POST.get("host")
        
        app_list = managable_app(request.session["authority_set"])
        
        appname_list = []
        for app in app_list:
            appname_list.append(app.app_name)
        
        res_list = Notification.objects.filter(appname__in=appname_list).order_by('-time')
        
        if app_id:
            appname = AppService.objects.get(id=app_id).app_name
            res_list = res_list.filter(appname=appname)
        
        if host_ip:
            res_list = res_list.filter(host=ip2host(host_ip))
            
        paginator = Paginator(res_list, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
        
        host_list = [item.host for item in pager]
        ip_list = get_all_ip(host_list)
        for i in range(len(ip_list)):
            pager.object_list[i].host = ip_list[i]
            
        return render_to_response('notification/searchback.html', {'notification_list':pager})
    return HttpResponseBadRequest("错误请求")
    
    
@login_required
def hindex(request):
    return render_to_response('notification/host_event_index.html')
    
@login_required
def hsearch(request):
    if request.method =='POST':
        host_ip = request.POST.get("host_ip")
        
        res_list = HostEvent.objects.all().order_by('-time')
        
        if host_ip:
            res_list = res_list.filter(host=ip2host(host_ip))
            
        paginator = Paginator(res_list, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
        
        host_list = [item.host for item in pager]
        ip_list = get_all_ip(host_list)
        for i in range(len(ip_list)):
            pager.object_list[i].host = ip_list[i]
            
        return render_to_response('notification/host_event_searchback.html', {'notification_list':pager})
    return HttpResponseBadRequest("错误请求")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
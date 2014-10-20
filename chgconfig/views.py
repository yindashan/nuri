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



from authority.decorators import permission_required
import logging
from redissync.models import host2ip, ip2host
from chgconfig.models import host_offline, host_change_ip

# 显示主机配置或变更的操作界面
@login_required
def index(request):
    return render_to_response('chgconfig/index.html')

#@login_required
@permission_required('host_change')
def host_to_ip(request):
    if request.method == "POST":
        host_id = request.POST.get("host_id")
        ip = host2ip(host_id)
        return render_to_response('chgconfig/host_ip.html', {'host_id': host_id, 'ip':ip})
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
#@login_required    
@permission_required('host_change')    
def ip_to_host(request):
    if request.method == "POST":
        ip = request.POST.get("ip")
        host_id = ip2host(ip)
        return render_to_response('chgconfig/host_ip.html', {'host_id': host_id, 'ip':ip})
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
#@login_required    
@permission_required('host_change')
def changeip(request):
    logger = logging.getLogger("django")
    if request.method == "POST":
        host_id = request.POST.get("host_id")
        old_ip = request.POST.get("old_ip")
        new_ip = request.POST.get("new_ip")
        
        logger.info("接收到主机IP变更请求, 处理人: %s,主机ID: %s, 原IP: %s, 新IP: %s", 
            request.user.username, host_id, old_ip, new_ip)
        
        return render_to_response('chgconfig/result.html', {'action': "主机IP变更操作",
            'result':host_change_ip(host_id, old_ip, new_ip)})
        
    else:
        return  HttpResponseBadRequest(u"错误请求")
    
#@login_required      
@permission_required('host_change')
def offline(request):
    logger = logging.getLogger("django")
    if request.method == "POST":
        host_id = request.POST.get("host_id")
        logger.info("接收到主机下线请求, 处理人: %s,主机ID: %s", request.user.username, host_id)
        
        return render_to_response('chgconfig/result.html', {'action': "主机下线操作",
            'result':host_offline(host_id)})
    else:
        return  HttpResponseBadRequest(u"错误请求")
    
    
    
    
    

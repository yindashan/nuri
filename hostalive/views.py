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

from hostalive.models import AliveCheck, AliveRule, AliveCheckRepr
from utils.utils import filterIP
from redissync.models import get_host
from utils.constants import retry_dict, notify_dict
from authority.decorators import permission_required

@login_required
def index(request):
    items = AliveCheck.objects.order_by('id')

    paginator = Paginator(items, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    res_list = []
    for item in pager:
        res_list.append(AliveCheckRepr(item))
    pager.object_list = res_list
    
    return render_to_response('hostalive/index.html',{'record_list':pager})

#@login_required    
@permission_required('appitem_operate')
def add(request):
    rule_list = AliveRule.objects.all()
    if request.method == 'POST':
        ac = AliveCheck()
        ac.name = request.POST.get('name')
        ac.retry_count = request.POST.get('retry_count')
        ac.notify_interval = request.POST.get('notify_interval')
        ac.comment = request.POST.get('comment')
        ac.email_list = request.POST.get('email_list')
        ac.mobile_list = request.POST.get('mobile_list')
        ip_list = request.POST.get('ip_list')
        # 过滤IP列表防止出现重复的IP地址         
        ip_list = filterIP(ip_list.split(','))
        host_list = get_host(ip_list)
        ac.ip_list = ','.join(ip_list)
        ac.host_list = ','.join(host_list)
        ac.save()
        
        rule_list = request.POST.getlist('rules')
        for rule in rule_list:
            # 规则
            ac.aliverule_set.add(int(rule))
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/hostalive/index", "message":u'添加成功'}),
            mimetype='application/json')
        
    else:   
        return render_to_response('hostalive/add.html',{'rule_list':rule_list})
        
# 删除记录
#@login_required
@permission_required('appitem_operate')
def delete(request, criterion_id):
    criterion = None
    try:
        criterion = AliveCheck.objects.get(id=int(criterion_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此判断标准不存在!'}), mimetype='application/json')
    
    criterion.aliverule_set.clear()
    # 删除此角色
    criterion.delete()
    
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/hostalive/index", "message":u'删除成功'}),
        mimetype='application/json')

#@login_required
@permission_required('appitem_operate')
def edit(request, criterion_id):
    criterion = None
    try:
        criterion = AliveCheck.objects.get(id=int(criterion_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此判断标准不存在!'}),
            mimetype='application/json')
            
    if request.method == 'POST':
        criterion.name = request.POST.get('name')
        criterion.retry_count = request.POST.get('retry_count')
        criterion.notify_interval = request.POST.get('notify_interval')
        criterion.comment = request.POST.get('comment')
        criterion.email_list = request.POST.get('email_list')
        criterion.mobile_list = request.POST.get('mobile_list')
        ip_list = request.POST.get('ip_list')
        # 过滤IP列表防止出现重复的IP地址         
        ip_list = filterIP(ip_list.split(','))
        host_list = get_host(ip_list)
        criterion.ip_list = ','.join(ip_list)
        criterion.host_list = ','.join(host_list)
        criterion.save()
        
        rule_list = request.POST.getlist('rules')
        criterion.aliverule_set.clear()
        for rule in rule_list:
            # 规则
            criterion.aliverule_set.add(int(rule))
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/hostalive/index", 
            "message":u'编辑成功'}),mimetype='application/json')
    
    else:
        item_list = criterion.aliverule_set.all()
        rule_id_list = [int(rule.id) for rule in item_list ]
        rule_list = AliveRule.objects.all()
        
        return render_to_response('hostalive/edit.html', {'rule_list':rule_list, 
            'criterion':criterion, 'rule_id_list':rule_id_list, 'retry_dict':retry_dict,
            'notify_dict':notify_dict})
    
    
    
    
    
    
    
    

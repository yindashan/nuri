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

# std lib
import logging

# our own lib
from business.models import BusinessLine, BnLineRepr
from appitem.models import AppService


# 显示应用列表
@login_required
def index(request): 
    items = BusinessLine.objects.order_by('name')
    paginator = Paginator(items, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    res_list = []
    for bn in pager:
        res_list.append(BnLineRepr(bn))
    pager.object_list = res_list
        
    return render_to_response('business/index.html',{'business_list':pager})
    
@login_required
def add(request):
    logger = logging.getLogger('django')
    
    if request.method == 'POST':
        bl = BusinessLine()
        bl.name = request.POST.get('bl_name')
        bl.comment = request.POST.get('comment')
        bl.op_interface = request.POST.get('op_interface')
        bl.op_phone = request.POST.get('op_phone')
        bl.bn_interface = request.POST.get('bn_interface')
        bl.bn_phone = request.POST.get('bn_phone')
        bl.save()
        
        # 保存业务线和应用之间的关联关系
        bl.apps.clear()
        app_id_list = request.POST.getlist('rel_app')
        for app_id in app_id_list:
            bl.apps.add(int(app_id))
        
        # 日志
        logger.info(u'【业务线】帐号:%s,创建业务线:%s成功。', request.user.username, bl.name)
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/business/index", "message":u'添加成功'}),
            mimetype='application/json')        
    else:
        app_list = AppService.objects.all()
        print len(app_list)
        return render_to_response('business/add.html', {'app_list':app_list}) 
        
@login_required
def edit(request, bn_id):
    logger = logging.getLogger('django')
    bl = None
    try:
        bl = BusinessLine.objects.get(id=int(bn_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'业务线记录不存在!'}),
            mimetype='application/json')
            
    if request.method == 'POST':
        bl.name = request.POST.get('bl_name')
        bl.comment = request.POST.get('comment')
        bl.op_interface = request.POST.get('op_interface')
        bl.op_phone = request.POST.get('op_phone')
        bl.bn_interface = request.POST.get('bn_interface')
        bl.bn_phone = request.POST.get('bn_phone')
        bl.save()
        
        # 保存业务线和应用之间的关联关系
        bl.apps.clear()
        app_id_list = request.POST.getlist('rel_app')
        for app_id in app_id_list:
            bl.apps.add(int(app_id))
        
        # 日志
        logger.info(u'【业务线】帐号:%s,修改业务线:%s成功。', request.user.username, bl.name)
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/business/index", "message":u'编辑成功'}),
            mimetype='application/json')   
    else:
        app_list = AppService.objects.all()
        selected_id_list = [ app.id for app in bl.apps.all()]
        return render_to_response('business/edit.html',  {'app_list':app_list, 'business':bl,
            'selected_id_list':selected_id_list})       
        
# 删除记录
@login_required
def delete(request, bn_id):
    logger = logging.getLogger('django')
    bl = None
    try:
        bl = BusinessLine.objects.get(id=int(bn_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'业务线记录不存在!'}),
            mimetype='application/json')
            
    # 删除关联关系        
    bl.apps.clear()
    # 删除业务线记录
    bl.delete()
    
    # 日志
    logger.info(u'【业务线】帐号:%s,删除业务线:%s成功。', request.user.username, bl.name)
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/business/index", "message":u'删除成功'}), 
        mimetype='application/json')
        
    
        
        
        
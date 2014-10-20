# -*- coding:utf-8 -*-

#django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db import connection

#standard library
import json

# our own code
from appitem.models import managable_app
from role.models import Role
from shownode.models import right_tree_struct, tree_structure, get_chart_list
from shownode.models import delete_node,update_node,append_node, config_chart
from django.conf import settings
from account.models import getUser
from utils.jsonhelp import complexObj2json


#显示组织机构视图
@login_required
def tree(request):
    #根节点id
    node_id = 1;
    #权限集合
    auth_set = request.session["authority_set"]
    tree_struct = tree_structure(node_id, auth_set, None, settings.CONTROL_LEVEL)
    node_list = []
    if tree_struct:
        node_list.append(tree_struct)
    return HttpResponse(json.dumps(node_list), mimetype="text/plain", status=200, content_type="text/plain")

# 用于配置读写权限
@login_required
def righttree(request):
    if request.GET:
        return HttpResponseBadRequest("错误请求");
    else:
        purpose = request.POST.get("purpose")
        role_id = request.POST.get("role_id")
        #根节点id
        node_id = 1;
        # 此角色的权限集合
        auth_set = set()
        # 如果编辑一个角色，role_id 不为None
        if role_id != None:
            role = Role.objects.get(id=int(role_id))
            for p in role.permissions.all():
                auth_set.add(p.codename)
                
        tree_struct = right_tree_struct(node_id, settings.CONTROL_LEVEL, purpose, auth_set)
        node_list = [tree_struct]
        return HttpResponse(json.dumps(node_list), mimetype="text/plain", status=200, content_type="text/plain")
    
@login_required
def manipulate_tree(request):
    if request.POST:
        dd = {}
        dd['status']='failure'
        action = request.POST.get('action')
        if action == 'append':
            parent_id = request.POST.get("parent_id")
            text = request.POST.get("text")
            id_array_str = request.POST.get("related_ids")
            node = append_node(parent_id,text,settings.CONTROL_LEVEL)
            
            if id_array_str:
                chart_id_list = [int(item) for item in id_array_str.split(',')]
                config_chart(node.id, chart_id_list)
            
            dd['node_id']=node.id;
        elif action == 'update':
            node_id = request.POST.get("node_id")
            text = request.POST.get("text")
            id_array_str = request.POST.get("related_ids")
            update_node(node_id,text)
            
            if id_array_str:
                chart_id_list = [int(item) for item in id_array_str.split(',')]
                config_chart(node_id, chart_id_list)
            
        elif action == 'delete':
            node_id = int(request.POST.get('node_id'))
            delete_node(node_id)
        dd['status']='success'
        return HttpResponse(content=json.dumps(dd), content_type='text/plain')
    return HttpResponseBadRequest("错误请求");

# 节点当前已经关联的图表
@login_required
def get_relation(request):
    if request.method == "GET":
        node_id = int(request.GET.get("node_id"));
        dd = {}
        dd['single_charts'] = get_chart_list(node_id, None, None)
        return HttpResponse(json.dumps(complexObj2json(dd)))
    return HttpResponseBadRequest("错误请求");  

# 获取node所对应的监控项图表  前台点击节点时触发此函数
@login_required
def display(request):
    if request.method == 'GET':
        node_id = request.GET.get('node_id',1);
        return render_to_response('shownode/display.html', {'node_id': node_id}) 
    return  HttpResponseBadRequest("错误请求")

@login_required
def getchart(request):
    if request.method == 'GET':
        node_id = int(request.GET.get('node_id',1))
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        chart_list = get_chart_list(node_id, start_time, end_time)
        return render_to_response('showchart/charts.html', {'chart_list': chart_list})    
    return  HttpResponseBadRequest("错误请求")

# 展示业务视图页面
@login_required 
def businessview(request):
    if request.method == 'GET':
        # 部分应用中监控项读权限
        auth_set = request.session["authority_set"]
        # 可以对其监控项进行读操作的应用
        app_list = managable_app(auth_set)
        user = getUser(request.user.id)  
        return render_to_response('shownode/businessview.html', {'user':user, 'app_list':app_list})    
    return  HttpResponseBadRequest("错误请求")
    
    
    
    
    
    

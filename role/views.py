# -*- coding:utf-8 -*-

# django library
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required


# our own code
from authority.models import Permission
from role.models import Role
from log.models import Log
from utils.constants import permission_type_dict

# 显示用户列表
@login_required
def index(request):
    roles = Role.objects.all()
    paginator = Paginator(roles, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('role/index.html',{'role_list':pager})

# 删除记录
@login_required
def delete(request, role_id):
    role = None
    try:
        role = Role.objects.get(id=int(role_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此角色不存在!'}), mimetype='application/json')
    # 删除角色和人的关联关系
    role.users.clear()
    # 删除角色和权限的关联关系
    role.permissions.clear()
    # 删除此角色
    role.delete()
    
    # 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 2
    log.relate_id = role.id
    log.content="execute delete role " + role.name + " success!"
    log.level = 1
    log.save()
    
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/role/index", "message":u'删除成功'}), mimetype='application/json')

@login_required
def add(request):
    pdict = {}
    for key in permission_type_dict:
        if key != 4:    # 节点权限的配置另外实现
            pdict[permission_type_dict[key]]=Permission.objects.filter(type=key).order_by('id')
    
    if request.POST:
        role_name = request.POST.get("role_name")
        role_desc = request.POST.get("role_desc")
        permission_id_list = request.POST.getlist("permission_id")
        #　保存角色信息
        role = Role();
        role.name = role_name
        role.desc = role_desc
        role.save()
        # 保存角色和权限对应关系
        for pid in permission_id_list:
            role.permissions.add(pid)
        
        # 日志
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 2
        log.relate_id = role.id
        log.content="execute add role " + role.name + " success!"
        log.level = 1
        log.save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/role/index", "message":u'添加成功'}), 
            mimetype='application/json')
    return render_to_response('role/add.html',{'pdict':pdict})

# 编辑
@login_required
def edit(request, role_id):
    pdict = {}
    for key in permission_type_dict:
        # 节点权限的配置另外实现
        if key != 4:    
            pdict[permission_type_dict[key]] = Permission.objects.filter(type=key).order_by('id')
            print pdict[permission_type_dict[1]]
    role = Role.objects.get(id=int(role_id))#把具体的角色管理中所对应的角色名称取出来
    
    permission_id_list = [] 
    for p in role.permissions.all():
        permission_id_list.append(p.id)
    
    if request.POST:
        role_name = request.POST.get("role_name")
        role_desc = request.POST.get("role_desc")
        permission_id_list = request.POST.getlist("permission_id")
        #保存角色信息
        role.name = role_name
        role.desc = role_desc
        role.save()
        # 保存角色和权限对应关系
        role.permissions.clear()
        for pid in permission_id_list:
            role.permissions.add(pid)
        
        # 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 2
        log.relate_id = role.id
        log.content = "execute edit role " + role.name + " success!"
        log.level = 1
        log.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/role/index", "message":u'编辑成功'}),
            mimetype='application/json')  
    return render_to_response('role/edit.html', {"pdict":pdict, "role": role, "permission_id_list":permission_id_list},
			        context_instance=RequestContext(request))

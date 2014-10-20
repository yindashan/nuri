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
from account.models import UserProfile 
from account.models import getUser,user2Extend
from dynamicconfig.models import validate_ldap
from role.models import Role 
from log.models import Log


# 显示用户列表
@login_required
def index(request):
    users = User.objects.order_by('username')
    paginator = Paginator(users, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
    pager.object_list = user2Extend(pager.object_list)
    return render_to_response('account/index.html',{'user_list':pager}, context_instance=RequestContext(request))

# 删除记录
@login_required
def delete(request, user_id):
    user = None
    try:
        user = User.objects.get(id = int(user_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400,"message":u'此用户不存在!'}), mimetype='application/json')
    # 删除用户对应的扩展表 UserProfile 中的记录
    UserProfile.objects.get(user_id = user.id).delete()
    # 删除此用户与角色的关联关系
    user.role_set.clear()
    # 删除此用户与权限的关联关系
    user.permission_set.clear()
    # 删除此用户
    user.delete()
    # 日志
    Log(username=request.user.username,log_type=1,relate_id=user_id,content="execute delete user " + user.username + " success!", level=1).save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/account/index", "message":u'删除成功'}), mimetype='application/json')

@login_required
def add(request):
    role_list = Role.objects.all()
    if request.POST:
        username = request.POST.get("username")
        realname = request.POST.get("realname")
        email = request.POST.get("email")
        roles = request.POST.getlist("role")
        department = request.POST.get("department")
        phone = request.POST.get("phone")
        # 验证重复的帐号名
        usernames = User.objects.filter(username__iexact=username)
        # 验证重复的邮件地址
        emails = User.objects.filter(email__iexact=email)
        
        if usernames:
            return HttpResponse(simplejson.dumps({"statusCode":403,  "message":u'用户名已经存在不能添加'}), mimetype='application/json')
        if emails:
            return HttpResponse(simplejson.dumps({"statusCode":403,  "message":u'邮件地址已经存在不能添加'}), mimetype='application/json')
        # 验证用户名是否存在于LDAP中
        if not validate_ldap(username):
            return HttpResponse(simplejson.dumps({"statusCode":403,  "message":u'用户名无效不能添加'}), mimetype='application/json')
        
        # 保存用户信息
        # 密码由用户名单向散列得到,实际登录时使用LADP 验证真正的用户名和密码
        password = make_password(username, salt=None, hasher='default')
        
        user = User(username=username, email=email,password=password)
        user.save()
        userprofile = UserProfile(user=user, department=department, phone=phone,realname=realname)
        userprofile.save()
        
        # 保存角色信息 
        for item in roles:
            user.role_set.add(int(item))
        
        # 日志
        Log(username=request.user.username,log_type=1,relate_id=user.id,content="execute add user " + user.username + " success!", level=1).save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/account/index", "message":u'添加成功'}), mimetype='application/json')
    
    return render_to_response('account/add.html',{'role_list':role_list},context_instance=RequestContext(request))

# 编辑
@login_required
def edit(request, user_id):
    user = getUser(int(user_id));
    role_list = Role.objects.all()
    if not user:
        return HttpResponseBadRequest("错误请求")
    if request.POST:
        department = request.POST.get("department")
        realname = request.POST.get("realname")
        phone = request.POST.get("phone")
        roles = request.POST.getlist("role")
        userprofile = UserProfile.objects.get(user_id = user.id)
        userprofile.department = department
        userprofile.phone = phone
        userprofile.realname = realname
        userprofile.save()
        
        #重置角色信息
        auth_user = User.objects.get(id=int(user_id))
        auth_user.role_set.clear()
        for item in roles:
            auth_user.role_set.add(int(item))
        
        # 日志
        Log(username=request.user.username,log_type=1,relate_id=user_id,content="execute edit user " + user.username + " success!", level=1).save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/account/index", "message":u'编辑成功'}), mimetype='application/json')  
    return render_to_response('account/edit.html', {'user': user,'role_list':role_list},context_instance=RequestContext(request))


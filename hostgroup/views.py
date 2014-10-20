#!usr/bin/env python
# -*- coding:utf-8 -*-

import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required

from iptools.ipv4 import ip2long, long2ip

from log.models import Log
from utils.utils import isIP
from hostgroup.models import get_all_host_group_info, get_all_host
from hostgroup.models import get_host_group_relation_by_gid, get_host_group_info_by_id, get_host_group_info_exclude_id, get_host_in_ip
from hostgroup.models import add_host_group_relation, edit_host_group_relation, search_host_group, move_to_save_model, host_group_info_save
from hostgroup.models import gen_copy_from_host_group_relation

@login_required
def index(request):
    return render_to_response('hostgroup/index.html')

# TODO: 修改权限
@login_required
def add(request):
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        group_desc = request.POST.get("group_desc")
        ip_list = request.POST.get("ip_list")
        
        # 1. 保存host_group_info表
        error_message = host_group_info_save(group_name, group_desc)
        if error_message != "":
            return HttpResponse(simplejson.dumps({"statusCode":400, "message": error_message}), mimetype='application/json')
        
        # 2. 保存host_group_relation表
        add_host_group_relation(group_name, ip_list)
        
        # 3. 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 0
        log.content="execute add group " + group_name + " " + group_desc + " success!"
        log.level = 1
        log.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/hostgroup/index", "message":u'添加成功'}), mimetype='application/json')        
    else:
        return render_to_response('hostgroup/add.html', {'hostgroup_list': get_all_host_group_info()}) 

# TODO: 修改权限
@login_required
def edit(request, item_id):
    item_id = int(item_id)
    
    # 取得原来的主机列表
    old_ip_list = []
    item_hosts = get_host_group_relation_by_gid(item_id)
    for host in item_hosts:
        old_ip_list.append(host.host.host_ip)
    
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        group_desc = request.POST.get("group_desc")
        new_ip_list = request.POST.get("ip_list")
        new_ip_list = split_list(new_ip_list)
        
        # 1. 保存host_group_info表
        error_message = host_group_info_save(group_name, group_desc, item_id=item_id)
        if error_message != "":
            return HttpResponse(simplejson.dumps({"statusCode":400, "message": error_message}), mimetype='application/json')
        
        # 2. 保存host_group_relation表
        edit_host_group_relation(item_id, new_ip_list, old_ip_list)
        
        # 3. 日志
        log = Log()
        log.username = request.user.username
        log.log_type = 0
        log.content="execute edit group " + group_name + " " + group_desc + " success!"
        log.level = 1
        log.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/hostgroup/index", "message":u'编辑成功'}), mimetype='application/json')        
    else:
        item_info = get_host_group_info_by_id(item_id)
        host_group_list = get_host_group_info_exclude_id(item_id)
        
        old_ip_list = ip_sort(old_ip_list)
        ip_range_list = gen_ip_range_list(old_ip_list)
        old_ip_list = ','.join(old_ip_list)
        return render_to_response('hostgroup/edit.html', {'hostgroup_list': host_group_list, 'item_info': item_info, 'ip_list': old_ip_list, 'ip_range_list': ip_range_list}) 

# TODO: 修改权限
@login_required
def delete(request, item_id):
    item_id = int(item_id)
    
    # 1. 删除host_group_info表
    item  = None
    try:
        item = get_host_group_info_by_id(item_id)
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'主机组不存在!'}), mimetype='application/json')
    item.delete()
    
    # 2. 删除host_group_relation表
    host_group_relation = get_host_group_relation_by_gid(item_id)
    host_group_relation.delete()

    # 3. 日志
    log = Log()
    log.username = request.user.username
    log.log_type = 0
    log.content="execute delete hostgroup " + item.name + " success!"
    log.level = 1
    log.save()
    
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/hostgroup/index", "message":u'删除成功'}), mimetype='application/json')

@login_required
def watch(request, item_id):
    item_id = int(item_id)
    try:
        host_group_info = get_host_group_info_by_id(item_id)
    except:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'主机组不存在!'}), mimetype='application/json')
    
    # 取得IP列表
    host_group_relation = get_host_group_relation_by_gid(item_id)
    ip_list = []
    for host in host_group_relation:
        ip_list.append(host.host.host_ip)
    
    # 排序
    ip_list = ip_sort(ip_list)
    
    # 将IP分成连续段
    ip_range_list = gen_ip_range_list(ip_list)
            
    return render_to_response('hostgroup/watch.html', {'host_group_info': host_group_info, 'ip_range_list': ip_range_list}) 


# TODO: 修改权限
@login_required
def search(request):
    if request.method == "POST":
        name_or_desc = request.POST.get("name_or_desc")
        ip = request.POST.get("ip")
        
        hostgroup_list = search_host_group(name_or_desc, ip)
        
        # 分页
        paginator = Paginator(hostgroup_list, 10)
        currentPage = request.POST.get('pageNum',1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
                
        return render_to_response('hostgroup/searchback.html', {'hostgroup_list':pager})
    else:
        return HttpResponseBadRequest("错误请求")

@login_required
def change_host_search(request):
    if request.method == "GET":
        old_ip_list = request.GET.get("ip_list")
        old_ip_list = split_list(old_ip_list)
        ip_list = {"available_ip": [], "chosen_ip": old_ip_list}
        
        # 取得可用的IP列表
        host_list = get_all_host()
        for host in host_list:
            ip_list["available_ip"].append(host.host_ip)
        ip_list["available_ip"].extend(old_ip_list)  # 显示虽然不在host表中，但在ip_list里面的主机，方便删除
        ip_list["available_ip"] = list(set(ip_list["available_ip"]))
        
        # 排序
        ip_list["available_ip"] = ip_sort(ip_list["available_ip"])
        ip_list["chosen_ip"] = ip_sort(ip_list["chosen_ip"])
        
        return HttpResponse(json.dumps(ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")
    
@login_required
def copy_from_search(request):
    if request.method == "GET":
        gid = request.GET.get("gid")
        ip_list = request.GET.get("ip_list")
        ip_list = split_list(ip_list)
        
        res_ip_list = []
        if gid != "":
            hosts = get_host_in_ip(ip_list)
            hid_list = []
            for host in hosts:
                hid_list.append(host.id)
            
            host_group_relation = gen_copy_from_host_group_relation(gid, hid_list)
            
            for host in host_group_relation:
                res_ip_list.append(host.host.host_ip)
        
            # 排序
            res_ip_list = ip_sort(res_ip_list)
        
        return HttpResponse(json.dumps(res_ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")
    
@login_required
def move_to_search(request):
    if request.method == "GET":
        gid = request.GET.get("gid")
        saved_ip_list = request.GET.get("saved_ip_list")
        saved_ip_list = split_list(saved_ip_list)
        
        if gid != "":
            ip_list_of_cur_group = []
            hosts = get_host_group_relation_by_gid(gid)
            for host in hosts:
                ip_list_of_cur_group.append(host.host.host_ip)
            
            res_ip_list = list(set(saved_ip_list) - set(ip_list_of_cur_group))
        else:
            res_ip_list = saved_ip_list
        
        # 排序
        res_ip_list = ip_sort(res_ip_list)
        
        return HttpResponse(json.dumps(res_ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")

# TODO: 修改权限
@login_required
def change_host_save(request):
    if request.method == "POST":
        new_ip_list = request.POST.get("new_ip_list")
        new_ip_list = split_list(new_ip_list)
        new_ip_list = ip_sort(new_ip_list)
        res_ip_list = {"ip_list": new_ip_list, "ip_range_list": gen_ip_range_list(new_ip_list)}
        return HttpResponse(json.dumps(res_ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")
    
# TODO: 修改权限
@login_required
def copy_from_save(request):
    if request.method == "POST":
        old_ip_list = request.POST.get("old_ip_list")
        new_ip_list = request.POST.get("new_ip_list")
        
        old_ip_list = split_list(old_ip_list)
        new_ip_list = split_list(new_ip_list)
        
        ip_list = list(set(old_ip_list + new_ip_list))
        ip_list = ip_sort(ip_list)
        res_ip_list = {"ip_list": ip_list, "ip_range_list": gen_ip_range_list(ip_list)}
        return HttpResponse(json.dumps(res_ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")

# TODO: 修改权限
@login_required
def move_to_save(request):
    if request.method == "POST":
        cur_gid = request.POST.get("cur_gid")
        move_to_gid = request.POST.get("move_to_gid")
        move_type = request.POST.get("move_type")
        old_ip_list = request.POST.get("old_ip_list")
        saved_ip_list = request.POST.get("saved_ip_list")
        move_ip_list = request.POST.get("move_ip_list")
        
        old_ip_list = split_list(old_ip_list)
        saved_ip_list = split_list(saved_ip_list)
        move_ip_list = split_list(move_ip_list)
        
        ip_list, saved_ip_list = move_to_save_model(cur_gid, move_to_gid, move_type, old_ip_list, saved_ip_list, move_ip_list)
        ip_list = ip_sort(ip_list)
        saved_ip_list = ip_sort(saved_ip_list)
        res_ip_list = {"ip_list": ip_list, "saved_ip_list": saved_ip_list, "ip_range_list": gen_ip_range_list(ip_list)}
        return HttpResponse(json.dumps(res_ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")

# TODO: 修改权限
@login_required
def manual_add_save(request):
    if request.method == "POST":
        old_ip_list = request.POST.get("old_ip_list")
        manual_ip_list = request.POST.get("manual_ip_list")
        
        old_ip_list = split_list(old_ip_list)
        manual_ip_list = split_list("".join(manual_ip_list.split()))
        
        new_ip_list = []
        wrong_ip_list = []
        
        # 1. 去除非法IP
        for ip in manual_ip_list:
            if isIP(ip) is not None:
                new_ip_list.append(ip)
            else:
                wrong_ip_list.append(ip)
        
        # 2. 将新IP列表和旧列表合并
        new_ip_list = list(set(new_ip_list + old_ip_list))
        
        # 3. 排序
        new_ip_list = ip_sort(new_ip_list)
        
        res_ip_list = {"ip_list": new_ip_list, "wrong_ip_list": wrong_ip_list, "ip_range_list": gen_ip_range_list(new_ip_list)}
        
        return HttpResponse(json.dumps(res_ip_list))
    else:
        return HttpResponseBadRequest(u"错误请求")


# 字符串非空则spilt，否则返回空列表
def split_list(string):
    return string.split(',') if string != "" else []

# IP排序
def ip_sort(ip_list):
    long_ip_list = [ip2long(ip) for ip in ip_list]
    long_ip_list.sort()
    return [long2ip(ip) for ip in long_ip_list]

# 生成连续的IP段
def gen_ip_range_list(sorted_ip_list):
    ip_range_list = []
    
    if sorted_ip_list != []:
        ip_range_list.append({'start_ip': sorted_ip_list[0], 'type': 'single'})
        last_ip = sorted_ip_list[0]
        
        for ip in sorted_ip_list[1:]:
            if ip2long(ip) - ip2long(last_ip) == 1:
                i = len(ip_range_list) - 1
                ip_range_list[i]['end_ip'] = ip
                ip_range_list[i]['type'] = 'continuous'
            else:
                ip_range_list.append({'start_ip': ip, 'type': 'single'})
            last_ip = ip
    
    return ip_range_list
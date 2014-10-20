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

from hardware.models import export_hardware_info
from authority.decorators import permission_required

# 显示主机配置或变更的操作界面
@login_required
def index(request):
    return render_to_response('hardware/index.html')

#@login_required
@permission_required('host_hard_exp')
def export(request):
    if request.method == "GET":
        filename = u"主机硬件信息"
        filename = filename.encode('gbk')
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'  
        response.mimetype = 'text/csv'
        
        # 直接拼装一个csv字符串
        # 行中以","分隔, 每行以"\n" 分隔
        res = []
        line1 = []
        # machine
        line1.extend([u'生产厂商', u'型号', u'序列号'])
        # os
        line1.extend([u'OS类型', u'OS位数', u'OS版本'])
        # ip
        line1.extend([u'管理IP', u'内网IP', u'外网IP',u'是否Bond',u'DNS服务器'])
        # cpu
        line1.extend([u'生产厂商', u'型号', u'内核数',u'数量'])
        # mem
        line1.extend([u'生产厂商', u'型号', u'容量（G）',u'数量'])
        
        res.append(','.join(line1))
        
        item_list = export_hardware_info()
        for item in item_list:
            temp = []
            temp.extend([item.machine_mf, item.machine_model, item.machine_sn])
            temp.extend([item.os_type, item.os_bit, item.os_version])
            temp.extend([item.manage_ip, item.private_ip, item.public_ip, str(item.is_bond), item.nameserver])
            
            temp.extend([item.processor_mf, item.processor_model,
                item.processor_cores, item.processor_number])
            
            mem_info = item.mem_list[0]
            
            temp.extend([mem_info.mem_mf, mem_info.mem_model,
                str(float(mem_info.mem_size)/1024), mem_info.mem_number])
            
            res.append(','.join(temp))
        
        content = '\n'.join(res)
        response.content = content.encode('gbk')
        
        return response
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
        
        

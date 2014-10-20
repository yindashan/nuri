# -*- coding:utf-8 -*-
# 所有主机和硬件报警都通过此模块发出
import json
from celery import task
from utils.sms import sms
from utils.mail import send_mail
from appitem.models import AppService, AppRelation
from datetime import datetime
from django.conf import settings


# 异步处理主机存活事件的通知
@task
def notify_host(criterion, host, state, now_time):
    # 1. 产生通知信息
    dd = {}
    dd['time'] = now_time.strftime('%Y-%m-%d %H:%M:%S')
    dd['host'] = host
    if state == 'UP':
        dd['type'] = 'RECOVERY'
        dd['information'] = 'OK - The host is up now.'
    else:
        dd['type'] = 'PROBLEM'
        dd['information'] = 'CRITICAL - The host may be down.'
    dd['state'] = state
    
    settings.REDIS_DB.rpush('host_event', json.dumps(dd))
    
    # 2. 触发报警
    host_ip = settings.REDIS_DB.hget('host_ip', host)
    message = "%s Host Alert: IP: %s is %s" % (dd['type'], host_ip, state)
    
    if criterion.email_list:
        send_mail(u'技术支持中心--运维监控中心', criterion.email_list.split(','), message, message)
    
    if criterion.mobile_list:
        sms(criterion.mobile_list.split(','), message)

# 向应用的业务运维 发出 主机up/down 事件报警      
def alert_host4app(appname, host_ip, ntype, state):
    message = "%s Host Alert: IP: %s for %s is %s" % (ntype, host_ip, appname, state)
    try:
        app = AppService.objects.get(app_name = appname)
    except BaseException:
        return 
    
    email_list = change(app.email_list)
    mobile_list = change(app.mobile_list)
    # 当前逻辑, 子应用会继承父应用的报警人信息
    # 获取自己的父应用--单继承
    rel_list = AppRelation.objects.filter(child_app=app)
    for item in rel_list:
        email_list.extend(change(item.parent_app.email_list))
        mobile_list.extend(change(item.parent_app.mobile_list))
    
    if email_list:
        send_mail(u"技术支持中心--运维监控中心", email_list, message, message)
        
    if mobile_list:
        sms(mobile_list, message)

# 如果item_list 是逗号分隔的字符串，就返回一个列表
# 否则返回一个空列表
def change(item_list):
    item_list = item_list.strip()
    if item_list:
        return item_list.split(',')
    return []        



# 异步处理应用事件的通知
# 异步处理应用报警    
@task     
def notify_app(appname, host, ntype, state, info):
    # 1. 产生应用通知信息
    dd = {}
    dd['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dd['host'] = host
    dd['appname'] = appname
    dd['type'] = ntype
    dd['state'] = state
    dd['information'] = info
    
    settings.REDIS_DB.rpush('notification', json.dumps(dd))
    
    # 2. 触发报警
    # 检查主机状态，如果主机状态down, 则将主机事件发给应用的报警人
    # 其它情况正常发送应用报警短信
    app = None
    try:
        app = AppService.objects.get(app_name=appname)
    except BaseException:
        # FIXME
        return 
    if app.is_alarm == 1 :
        status = settings.REDIS_DB.hget('host_alive_' + host, 'current_status')
        host_ip = settings.REDIS_DB.hget('host_ip', host)
        if status is None or status == 'UP':
            alert_app(appname, host_ip, ntype, state, info)
        else:
            alert_host4app(appname, host_ip, 'PROBLEM', 'DOWN')
    
    
def alert_app(appname, host_ip, ntype, state, info):
    app = None
    try:
        app = AppService.objects.get(app_name = appname)
    except BaseException:
        return 
    
    email_list = change(app.email_list)
    mobile_list = change(app.mobile_list)
    # 当前逻辑, 子应用会继承父应用的报警人信息
    # 获取自己的父应用--单继承
    rel_list = AppRelation.objects.filter(child_app=app)
    for item in rel_list:
        email_list.extend(change(item.parent_app.email_list))
        mobile_list.extend(change(item.parent_app.mobile_list))
    
    if email_list:
        alert_app_mail(appname, host_ip, ntype, state, info, email_list)
    # 当前只有 CRITICAL 才触发短信报警  
    if state == 'CRITICAL' and mobile_list:
        alert_app_sms(appname, host_ip, ntype, state, mobile_list)
      

# 应用邮件通知    
def alert_app_mail(appname, host_ip, notify_type, state, info, email_list):
    subject = gen_subject(appname, host_ip, notify_type, state)
    content = gen_mail_content(appname, host_ip, notify_type, state, info)
    # 发送邮件
    content = content.replace('\\n','\n')
    
    if email_list:
        send_mail(u"技术支持中心--运维监控中心", email_list, subject, content)
        
# 应用短信通知   
def alert_app_sms(appname, host_ip, notify_type, state, mobile_list):
    message = gen_subject(appname, host_ip, notify_type, state)
        
    if mobile_list:
        sms(mobile_list, message)
    
def gen_subject(appname, host_ip, notify_type, state):
    subject = "***%s Service Alert: %s / %s is %s***" % (notify_type, host_ip, appname, state)
    return subject
    
def gen_mail_content(appname, host_ip, notify_type, state, info):
    ll = []
    ll.append("Notification Type: %s\n" % notify_type)
    ll.append("Service: %s\n" % appname)
    ll.append("Host: %s\n" % host_ip)
    ll.append("State: %s\n" % state)
    curr_time = datetime.now()
    ll.append("Date/Time: %s\n" % curr_time.strftime("%Y-%m-%d %H:%M:%S"))
    ll.append("\n")
    ll.append("Additional Info:\n")
    if info:
        ll.append(info)
    else:
        ll.append("null")

    return ''.join(ll)
    
    
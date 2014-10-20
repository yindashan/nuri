# Create your views here.
# -*- coding:utf-8 -*

import time
import math
import redis

from django.conf import settings
from django.http import  HttpResponseBadRequest
from django.shortcuts import render_to_response

from models import connect_redis,get_host_ip,get_host_alive,trans_list,get_host_total,get_appname



def format_time(s):
    tmp1 = s.split()
    t = []
    for item in tmp1[0].split('-'):
        t.append(item)
    for item in tmp1[1].split(':'):
        t.append(item)
    return t

def str_num(list_time):
    num_list = []
    for item in list_time:
        num_list.append(long(item))
    for i in range(0,3):
        num_list.append(0)
    return num_list   

def count_time(start_list_time,end_list_time):
    start_time_num = str_num(start_list_time)
    end_time_num = str_num(end_list_time)
    t0 = time.mktime(end_time_num) - time.mktime(start_time_num)
    return t0

def get_time_gap(l):
    start_list_time = format_time(l[1]) 
    end_list_time = format_time(time.strftime('%Y-%m-%d %H:%M:%S'))
    
    last_time_second = count_time(start_list_time,end_list_time)
    s= '持续   '
    n = last_time_second/60/60/24
    days = int(math.floor(n))
    s = s + str(days)+'天:'
    n = n - days
    
    hours = int(math.floor(n*24))
    s = s+ str(hours)+'小时:'
    n = n*24 - hours
    
    minutes = int(math.floor(n*60))
    s = s + str(minutes)+'分钟'
    l[1] = s
    return l
    
def reserve(lresult):
    l = []
    for item in lresult:
        b = []
        for i in range(0,len(item)):
            b.append(0)
        b[0] = item[0]
        b[len(b)-1] = item[1]
        b[1:len(b)-1] = item[2:len(item)]
        l.append(b)
    return l
def index(request):
    r = connect_redis()
    dict_host_ip = {}
    dict_host_alive = {}

    dict_host_ip = get_host_ip(r)
    dict_host_alive = get_host_alive(r,dict_host_ip)

    
    list_host_alive = []
    list_host_alive = trans_list(dict_host_alive)


    length = len(get_host_total())
    lresult=[]
    for item in list_host_alive:
        item = get_time_gap(item)
        lresult.append(item)
    lresult = get_appname(lresult)
    lresult = reserve(lresult)
    len_down = len(lresult)
    
     
    return render_to_response('showhostalive/index.html',{'list_host_alive':lresult,'length':length,'len_down':len_down})    

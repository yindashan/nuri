# -*- coding:utf-8 -*
import redis

from django.db import models

from nuri.settings import REDIS_HOST,REDIS_PORT,REDIS_PASSWORD,REDIS_DB_NUM 
from appitem.models import AppService, AppRelation
# Create your models here.


def connect_redis():
    r = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD,db=REDIS_DB_NUM)
    return r



def get_host_total():
    host_list = []
    app = AppService.objects.get(app_name='HOST_STATUS')
    host_list.extend(app.host_list.split(','))
    rel_list = AppRelation.objects.filter(parent_app=app)
    for rel in rel_list:
        temp = rel.child_app.host_list
        if temp:
            host_list.extend(temp.split(','))
    return host_list

def get_host_ip(r):
    dict_host_ip = {}
    list_ip_key = r.hkeys('host_ip')
    for item in list_ip_key:
        dict_host_ip[item] = r.hget('host_ip',item)
    return dict_host_ip

def get_appname(list_host_alive):
    for item in list_host_alive:
        apps = AppService.objects.filter(ip_list__icontains=item[0])
        item.append('应用名:')
        for a in apps:
            item.append(a.app_name)
    return list_host_alive 
   
def trans_list(dict_host_alive):
    list_host_alive = []
    for item in dict_host_alive:
        flag = 1

        l = []
        l.append(item)
        k = 0
        for i in dict_host_alive[item]:
            if i.strip()=='UP':
                flag = 0
                break
            if len(i)>1 and k!=0 and k!=3:
                l.append(i)
            k = k+1
        if flag == 1:
            list_host_alive.append(l)    
    return list_host_alive
    
def get_host_alive(r,dict_host_ip):
    
    dict_host_alive = {}
    list_host_before= list(r.keys('host_alive*'))
    list_host_after =[]

    for item in list_host_before:
        item = item[item.find('e')+2:]
        list_host_after.append(item)
    i = 0    
    for item in list_host_before:
        list_alive = []
        list_keys = list(r.hkeys(item))
        for key in list_keys:
            list_alive.append(r.hget(item,key))
        dict_host_alive[r.hget('host_ip',list_host_after[i])] = list_alive
        i = i+1
    return dict_host_alive 

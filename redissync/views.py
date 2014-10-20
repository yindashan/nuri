#!usr/bin/env python
#coding: utf-8
'''
Created on 2013-11-6

@author: jingwen.wu
'''
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from redissync.models import sync_config

from authority.decorators import permission_required

@login_required 
def index(request):
    return render_to_response('redissync/sync.html')
    
#@login_required     
@permission_required('sync_redis')
def redis_sync(request):
    flag = sync_config()
    return render_to_response('redissync/sync_return.html', {'flag': flag})

        


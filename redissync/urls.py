'''
Created on 2013-11-6

@author: zhu.wei
'''
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'redissync.views.index', name="redissync"),
    url(r'^index/$', 'redissync.views.index', name="redissync_index"),
    url(r'^redis_sync/$', 'redissync.views.redis_sync', name="redis_sync"),
)

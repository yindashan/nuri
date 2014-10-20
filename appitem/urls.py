#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'appitem.views.index', name="appitem"),
     url(r'^index/$', 'appitem.views.index', name="appitem_index"),
     url(r'^add/(?P<pid>-?\d+)/$', 'appitem.views.add', name="appitem_add"),
     url(r'^save/$', 'appitem.views.add_save', name="appitem_save"),
     url(r'^edit/(?P<app_id>\d+)/$', 'appitem.views.edit', name="appitem_edit"),
     url(r'^delete/(?P<app_id>\d+)/$', 'appitem.views.delete', name="appitem_delete"),
     url(r'^getappinfo/$', 'appitem.views.getappinfo', name="appitem_getappinfo"),
     url(r'^gethostinfo/$', 'appitem.views.gethostinfo', name="appitem_gethostinfo"),
     url(r'^search/$', 'appitem.views.search',name="appitem_search"),
     # 此应用的所有监控项
     url(r'^mitem/(?P<app_id>\d+)/$', 'appitem.views.mitem',name="appitem_mitem"),
     # 为某个应用激活它从父应用继承的监控项
     # 其原理为在子应用中，创建一个同名的监控项覆盖父应用中，此监控项的配置
     url(r'^active/(?P<appname>\w+)/(?P<mid>\d+)/$', 'appitem.views.active',name="appitem_active"),
     
     
)

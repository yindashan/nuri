# -*- coding:utf-8 -*-
#!usr/bin/env python

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'notification.views.index',name="notification"),
     # 应用事件通知
     url(r'^index/$', 'notification.views.index', name="notification_index"),
     url(r'^search/$', 'notification.views.search', name="notification_search"),
     
     # 主机事件通知 up/down
     url(r'^hindex/$', 'notification.views.hindex', name="notification_hindex"),
     url(r'^hsearch/$', 'notification.views.hsearch', name="notification_hsearch"),
)
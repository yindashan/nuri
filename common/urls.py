#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'common.views.index',name="common"),
     url(r'^index/$', 'common.views.index',name="common_index"),
     url(r'^login/$', 'common.views.login', name="common_login"),
     url(r'^logout/$', 'common.views.logout', name="common_logout"),
)
#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'business.views.index', name="business"),
     url(r'^index/$', 'business.views.index', name="business_index"),
     url(r'^add/$', 'business.views.add', name="business_add"),
     url(r'^edit/(?P<bn_id>\d+)/$', 'business.views.edit', name="business_edit"),
     url(r'^delete/(?P<bn_id>\d+)/$', 'business.views.delete', name="business_delete"),
)

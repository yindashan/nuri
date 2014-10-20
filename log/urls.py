#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'log.views.index',name="log"),
     url(r'^index$', 'log.views.index',name="log_index"),
)

#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^index/$', 'showhostalive.views.index', name="showhostalive_index"),
        )

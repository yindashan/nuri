#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^get_chart_id/$', 'showchart.views.get_chart_id', name="showchart_getChartId"),
    url(r'^quickshow/$', 'showchart.views.quickshow', name="showchart_quickshow"),
    url(r'^hostquickshow/$', 'showchart.views.hostquickshow', name="showchart_hostquickshow"),
    url(r'^simplechart/$', 'showchart.views.simplechart', name="showchart_simplechart"),
    
)
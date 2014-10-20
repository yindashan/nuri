#!usr/bin/env python

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'tcpinfo.views.index',name="tcpinfo"),
     url(r'^index/$', 'tcpinfo.views.index', name="tcpinfo_index"),
     url(r'^add/$', 'tcpinfo.views.add',name="tcpinfo_add"),
     url(r'^edit/(?P<tcp_id>\d+)/$', 'tcpinfo.views.edit',name="tcpinfo_edit"),
     url(r'^delete/(?P<tcp_id>\d+)/$', 'tcpinfo.views.delete',name="tcpinfo_delete"),
     url(r'^search/$', 'tcpinfo.views.search',name="tcpinfo_search"),
)
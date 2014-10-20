#!usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'monitorindex.views.index',name="monitorindex"),
     url(r'^index/$', 'monitorindex.views.index', name="monitorindex_index"),
     url(r'^add/$', 'monitorindex.views.add',name="monitorindex_add"),
     url(r'^edit/(?P<item_id>\d+)/$', 'monitorindex.views.edit',name="monitorindex_edit"),
     url(r'^delete/(?P<item_id>\d+)/$', 'monitorindex.views.delete',name="monitorindex_delete"),
     url(r'^watch/$', 'monitorindex.views.watch',name="monitorindex_watch"),
     url(r'^search/$', 'monitorindex.views.search',name="monitorindex_search"),
     url(r'^detail/(?P<host_id>\w+)/(?P<date>[\w\-]+)/$', 'monitorindex.views.detail',name="monitorindex_detail"),
)
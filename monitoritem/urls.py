#!usr/bin/env python

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'monitoritem.views.index',name="monitoritem"),
     url(r'^index/$', 'monitoritem.views.index', name="monitoritem_index"),
     url(r'^add/$', 'monitoritem.views.add',name="monitoritem_add"),
     url(r'^edit/(?P<item_id>\d+)/$', 'monitoritem.views.edit',name="monitoritem_edit"),
     url(r'^delete/(?P<item_id>\d+)/$', 'monitoritem.views.delete',name="monitoritem_delete"),
     url(r'^search/$', 'monitoritem.views.search',name="monitoritem_search"),
     url(r'^fetch_data/$', 'monitoritem.views.fetch_data',name="monitoritem_fetch_data"),
)
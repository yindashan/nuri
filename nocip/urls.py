#!usr/bin/env python

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'nocip.views.index',name="nocip"),
     url(r'^index/$', 'nocip.views.index', name="nocip_index"),
     url(r'^add/$', 'nocip.views.add',name="nocip_add"),
     url(r'^edit/(?P<nocip_id>\d+)/$', 'nocip.views.edit',name="nocip_edit"),
     url(r'^delete/(?P<nocip_id>\d+)/$', 'nocip.views.delete',name="nocip_delete"),
     url(r'^search/$', 'nocip.views.search',name="nocip_search"),
     #url(r'^fetch_data/$', 'urlinfo.views.fetch_data',name="urlinfo_fetch_data"),
)
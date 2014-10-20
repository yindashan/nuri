#!usr/bin/env python

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'urlinfo.views.index',name="urlinfo"),
     url(r'^index/$', 'urlinfo.views.index', name="urlinfo_index"),
     url(r'^add/$', 'urlinfo.views.add',name="urlinfo_add"),
     url(r'^edit/(?P<url_id>\d+)/$', 'urlinfo.views.edit',name="urlinfo_edit"),
     url(r'^delete/(?P<url_id>\d+)/$', 'urlinfo.views.delete',name="urlinfo_delete"),
     url(r'^search/$', 'urlinfo.views.search',name="urlinfo_search"),
     #url(r'^fetch_data/$', 'urlinfo.views.fetch_data',name="urlinfo_fetch_data"),
     url(r'^upload/$', 'urlinfo.views.upload',name="urlinfo_upload"),
)
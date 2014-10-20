#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'hostalive.views.index',name="hostalive"),
    url(r'^index/$', 'hostalive.views.index', name="hostalive_index"),
    url(r'^add/$', 'hostalive.views.add',name="hostalive_add"),
    url(r'^delete/(?P<criterion_id>\d+)/$', 'hostalive.views.delete',name="hostalive_delete"),
    url(r'^edit/(?P<criterion_id>\d+)/$', 'hostalive.views.edit',name="hostalive_edit"),
)

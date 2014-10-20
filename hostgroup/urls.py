#!usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'hostgroup.views.index',name="hostgroup"),
     url(r'^index/$', 'hostgroup.views.index', name="hostgroup_index"),
     url(r'^add/$', 'hostgroup.views.add',name="hostgroup_add"),
     url(r'^edit/(?P<item_id>\d+)/$', 'hostgroup.views.edit',name="hostgroup_edit"),
     url(r'^delete/(?P<item_id>\d+)/$', 'hostgroup.views.delete',name="hostgroup_delete"),
     url(r'^watch/(?P<item_id>\d+)/$', 'hostgroup.views.watch',name="hostgroup_watch"),
     url(r'^search/$', 'hostgroup.views.search',name="hostgroup_search"),
     url(r'^changehostsearch/$', 'hostgroup.views.change_host_search',name="hostgroup_changehostsearch"),
     url(r'^copyfromsearch/$', 'hostgroup.views.copy_from_search',name="hostgroup_copyfromsearch"),
     url(r'^movetosearch/$', 'hostgroup.views.move_to_search',name="hostgroup_movetosearch"),
     url(r'^changehostsave/$', 'hostgroup.views.change_host_save',name="hostgroup_changehostsave"),
     url(r'^copyfromsave/$', 'hostgroup.views.copy_from_save',name="hostgroup_copyfromsave"),
     url(r'^movetosave/$', 'hostgroup.views.move_to_save',name="hostgroup_movetosave"),
     url(r'^manualaddsave/$', 'hostgroup.views.manual_add_save',name="hostgroup_manualaddsave"),
)

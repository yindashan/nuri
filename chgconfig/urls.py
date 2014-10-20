#!usr/bin/env python

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'chgconfig.views.index',name="chgconfig_index"),
     url(r'^offline/$', 'chgconfig.views.offline', name="chgconfig_offline"),
     url(r'^changeip/$', 'chgconfig.views.changeip',name="chgconfig_changeip"),
     url(r'^host2ip/$', 'chgconfig.views.host_to_ip',name="chgconfig_host2ip"),
     url(r'^ip2host/$', 'chgconfig.views.ip_to_host',name="chgconfig_ip2host"),
)
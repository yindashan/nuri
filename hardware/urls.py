from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'hardware.views.index', name="hardware"),
    url(r'^index/$', 'hardware.views.index', name="hardware_index"),
    url(r'^export/$', 'hardware.views.export', name="hardware_export"),
)

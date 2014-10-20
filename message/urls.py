from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'message.views.index',name="message"),
     url(r'^index/$', 'message.views.index', name="message_index"),
)
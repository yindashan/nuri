from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    url(r'^$', 'common.views.index',name="index"),
    url(r'^loginpage/$','common.views.loginpage',name="loginpage"),
    url(r'^appitem/', include('appitem.urls')),
    url(r'^monitoritem/', include('monitoritem.urls')),
    url(r'^appitem/', include('appitem.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^common/', include('common.urls')),
    url(r'^role/', include('role.urls')),
    url(r'^log/', include('log.urls')),
    url(r'^redissync/', include('redissync.urls')),
    url(r'^shownode/', include('shownode.urls')),
    url(r'^showchart/', include('showchart.urls')),
    url(r'^message/', include('message.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^chgconfig/', include('chgconfig.urls')),
    url(r'^urlinfo/', include('urlinfo.urls')),
    url(r'^tcpinfo/', include('tcpinfo.urls')),
    url(r'^nocip/', include('nocip.urls')),
    url(r'^hardware/', include('hardware.urls')),
    url(r'^monitorindex/', include('monitorindex.urls')),
    url(r'^hostalive/', include('hostalive.urls')),
    url(r'^business/', include('business.urls')),
    url(r'^hostgroup/', include('hostgroup.urls')),
    url(r'^showhostalive/',include('showhostalive.urls')),
)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)

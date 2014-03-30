#encoding:utf-8
from django.conf.urls import patterns, url
from views import *

urlpatterns = patterns('whbus.views',
                       url(r'^$', Weixin.as_view()),
)

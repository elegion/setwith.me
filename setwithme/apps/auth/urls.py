# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('auth.views',
    url(r'^login/(?P<provider>anonymous|facebook|vkontakte)/$',
        'login',
        name='login'),
    url(r'^logout/$', 'logout', name='logout'),
)

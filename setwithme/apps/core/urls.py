# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('core.views',
    url(r'^$', 'home', name='home'),
    url(r'^lobby/$', 'lobby', name='lobby'),
)

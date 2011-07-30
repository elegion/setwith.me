# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('chat.views',
    url(r'^put_message/(?P<game_id>[\w]+)$', 'put_message'),
)

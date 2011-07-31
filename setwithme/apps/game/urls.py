# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('game.views',
    url(r'^create/$', 'start_game'),
    url(r'^game_screen/(?P<game_id>[\w]+)$', 'game_screen', name='game_screen'),
    url(r'^get_status/(?P<game_id>[\w]+)$', 'get_status'),
    url(r'^put_set_mark/(?P<game_id>[\w]+)$', 'put_set_mark'),
    url(r'^check_set/(?P<game_id>[\w]+)$', 'check_set'),
)

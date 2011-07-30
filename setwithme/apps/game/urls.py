# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('game.views',
    url(r'^waiting_screen/$', 'waiting_screen'),
    url(r'^game_screen/(?P<game_id>[\w]+)$', 'game_screen'),
    url(r'^create/$', 'start_game'),
    url(r'^status/(?P<game_id>[\w]+)$', 'status'),
    url(r'^$', 'waiting_screen', name='index'),
)

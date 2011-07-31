# -*- coding: utf-8 -*-
import uuid
from annoying.decorators import render_to
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST

from game.models import Game


@render_to('core/index.html')
def home(request):
    return {'players': User.objects.count(),
            'games_online': Game.objects.filter(finished=False).count()}


@render_to('core/lobby.html')
def lobby(request):
    return {
        'message': 'Set is designed by Marsha Falco in 1974 and published by Set Enterprises in 1991'
    }


@require_POST
def login(request):
    provider = request.POST.get('provider', '')
    if provider == 'anon':
        _anon_login(request)
    else:
        raise NotImplementedError('Provider %s login method not implemented' %
            provider)
    return redirect(lobby)


def logout(request):
    auth_logout(request)
    return redirect('/')


def _anon_login(request):
    user = authenticate()
    if user:
        auth_login(request, user)
        return True
    return False


def login_facebook(request):
    fb = request.facebook
    if fb and fb.uid and fb.graph:
        user = authenticate(
            fb_uid=fb.uid,
            fb_graphtoken=fb.access_token)
        auth_login(request, user)
    return redirect('/')

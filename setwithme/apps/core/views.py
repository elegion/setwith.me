# -*- coding: utf-8 -*-
from annoying.decorators import render_to
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST

from game.models import Game, GameSession, ClientConnectionState, Facts
from users.models import WaitingUser


@render_to('core/index.html')
def home(request):
    ONLINE_TIMEOUT = datetime.timedelta(minutes=30)
    now = datetime.datetime.now()
    guard = now - ONLINE_TIMEOUT
    return {'players': User.objects.filter(last_login__gt=guard).count(),
            'games_online': Game.objects.filter(finished=False).count()}


@login_required
@render_to('core/lobby.html')
def lobby(request):
    qs = GameSession.objects.\
        filter(user=request.user,
               left=False,
               game__finished=False).\
        exclude(client_state=ClientConnectionState.LOST)
    if qs.count():
        gs = qs.all()[0]
        return redirect('game_screen', game_id=gs.game.id)
    wu = WaitingUser.objects.get_or_create(user=request.user)[0].update()
    return {
        'message': Facts.objects.order_by('?')[0].text,
        'me': wu
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
    return redirect(lobby)

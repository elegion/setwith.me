# -*- coding: utf-8 -*-
import datetime

from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect

from game.models import ClientConnectionState, Facts, Game, GameSession
from users.models import UserProfile, WaitingUser


@render_to('core/index.html')
def home(request):
    ONLINE_TIMEOUT = datetime.timedelta(minutes=30)
    now = datetime.datetime.now()
    guard = now - ONLINE_TIMEOUT
    top_users = UserProfile.objects.order_by('-games_win', 'games_total')[:3]
    return {'players': User.objects.filter(last_login__gt=guard).count(),
            'games_online': Game.objects.filter(finished=False).count(),
            'top_users': top_users}


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

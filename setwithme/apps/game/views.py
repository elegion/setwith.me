# -*- coding: utf-8 -*-
import datetime
import json
import user

from annoying.decorators import ajax_request, render_to
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.cache import cache

from chat.models import ChatMessage
from game import constants
from game.models import (ClientConnectionState, Game,
                         GameSession, GameSessionState, get_uid)
from game.utils import Card, is_set
from users.models import WaitingUser


@render_to('game/game_screen.html')
def game_screen(request, game_id):
    game = Game.objects.get(id=game_id)
    users = [gs.serialize(request.user.id) for gs in \
        game.gamesession_set.all()]
    desc_cards = game.desk_cards_list
    rem_cards_cnt = len(game.rem_cards_list)
    initial_status = {'users': users,
                      'cards': [{'id': card_id,
                                'class': Card(id=card_id).as_text()} \
                                    for card_id in desc_cards],
                     'cards_left': rem_cards_cnt,
                     'game': {
                         'is_finished': game.is_finished(),
                         'leader': game.leader},
                     'chat': []}
    return {'game_id': game_id,
            'initial_status': json.dumps(initial_status, separators=(',', ':'))}


@ajax_request
def start_game(request):
    user = request.user
    qs = GameSession.objects.\
        filter(user=user,
               left=False,
               game__finished=False).\
        exclude(client_state=ClientConnectionState.LOST)
    if qs.count():
        gs = qs.all()[0]
        return {'status': 302,
                'url': reverse(game_screen, kwargs={'game_id': gs.game.id})}

    wu = WaitingUser.objects.get_or_create(user=user)[0].update()
    last_poll_guard = datetime.datetime.now() - constants.WAITING_USER_TIMEOUT

    opponents = WaitingUser.objects.\
        filter(last_poll__gt=last_poll_guard).\
        exclude(user=user).all()
    if not opponents:
        return {'status': 'polling',
                'opponents': []}

    now = datetime.datetime.now()
    join_timeout = request.session.get('game_join_timeout', None)
    if not join_timeout:
        join_timeout = request.session['game_join_timeout'] = now

    if join_timeout + constants.GAME_JOIN_WAIT_TIMEOUT > now:
        time_left = join_timeout + constants.GAME_JOIN_WAIT_TIMEOUT - now
        return {'status': 'polling',
                'timeout': time_left.seconds,
                'opponents': [op.serialize() for op in opponents]}

    game_id = get_uid()
    game = Game.objects.create(id=game_id)
    GameSession.objects.create(game=game, user=user)
    wu.delete()
    for op in opponents:
        GameSession.objects.create(game=game, user=op.user)
        op.delete()
    return {'status': '302',
            'url': reverse(game_screen, kwargs={'game_id': game_id})}


@ajax_request
def get_status(request, game_id):
    game = Game.objects.get(id=game_id)
    #update last access time
    gsession = GameSession.objects.get(game=game, user=request.user)
    gsession.update()

    #update game data
    now = datetime.datetime.now()
    state_pressed = gsession.state == GameSessionState.SET_PRESSED
    if state_pressed:
        if not gsession.set_pressed_dt or (gsession.set_pressed_dt and\
            ((now > gsession.set_pressed_dt + constants.PRESSED_SET_TIMEOUT))):
            for gs in game.gamesession_set.filter(state=GameSessionState.SET_ANOTHER_USER):
                gs.state = GameSessionState.NORMAL
                gs.save()
            gsession.state = GameSessionState.SET_PENALTY
            gsession.failures += 1
            gsession.save()
            update_status_cache(game_id)

#    if not gsession.game.gamesession_set.exclude(state=GameSessionState.SET_PENALTY).count():
#        gsession.game.gamesession_set.all().update(state=GameSessionState.NORMAL)

    expired = game.gamesession_set\
        .filter(state=GameSessionState.SET_PENALTY,
                set_pressed_dt__lte=now - constants.CLIENT_PENALTY_TIMEOUT)
    if len(expired):
        expired.update(state=GameSessionState.NORMAL)
        update_status_cache(game_id)

    if gsession.last_access + constants.CLIENT_LOST_TIMEOUT < now:
        gsession.client_state = ClientConnectionState.LOST
        gsession.save()
        update_status_cache(game_id)

    if gsession.last_access + constants.CLIENT_IDLE_TIMEOUT < now:
        gsession.client_state = ClientConnectionState.IDLE
        gsession.save()
        update_status_cache(game_id)

    status = cache.get('st_%s_%s' % (game_id, request.user.id))
    if not status:
        update_status_cache(game_id)

    return status


def update_status_cache(game_id):
    for gs in GameSession.objects.filter(game=game_id):
        cache.set('st_%s_%s' % (game_id, gs.user.id), calc_status(game_id, gs.user.id))


def calc_status(game_id, user_id):
    game = Game.objects.get(id=game_id)
    user = User.objects.get(id=user_id)

    chat_qs = ChatMessage.objects.filter(room=game)
    chat_qs = chat_qs.all()[0:10]

    users = [gs.serialize(user_id) for gs in \
        game.gamesession_set.all()]

    desc_cards = game.desk_cards_list
    desc_cards.extend(game.pop_cards(quantity=game.cards_to_pop - len(desc_cards)))

    rem_cards_cnt = len(game.rem_cards_list)

    return {'users': users,
            'cards': [{'id': card_id,
                       'class': Card(id=card_id).as_text()} \
                        for card_id in desc_cards],
            'cards_left': rem_cards_cnt,
            'game': {
                'has_sets': game.has_sets(),
                'sets_count': game.count_sets(),
                'is_finished': game.is_finished(),
                'leader': game.leader},
            'chat': [cm.get_serialized(user) for cm in chat_qs]}


def update_cache(f):
    """
    decorator, update cache on exit. Second param should be game_id
    """
    def inner(*args, **kwargs):
        result = f(*args, **kwargs)
        game_id = kwargs.get('game_id')
        if not game_id:
            game_id = args[1]
        update_status_cache(game_id)
        return result
    return inner


@ajax_request
@update_cache
def put_set_mark(request, game_id):
    game = Game.objects.get(id=game_id)
    if not game.gamesession_set.\
            filter(state=GameSessionState.SET_PRESSED).\
            count():
        gs = game.gamesession_set.get(user=request.user)
        gs.press_set()
        for g in game.gamesession_set.exclude(user=request.user).all():
            g.state = GameSessionState.SET_ANOTHER_USER
            g.save()
        return {'success': True}
    return {'success': False}


@ajax_request
@update_cache
def check_set(request, game_id):
    game = Game.objects.get(id=game_id)
    gs = game.gamesession_set.get(user=request.user)

    # Update status to IDLE for other game sessions:
    for gs_other in game.gamesession_set.exclude(user=request.user).all():
        gs_other.state = GameSessionState.NORMAL
        gs_other.save()

    def add_stat(gs, data):
        data.update({'sets_found': gs.sets_found,
                     'failures': gs.failures,
                     'score': gs.score})
        return data

    if gs.set_received_in_time():
        ids = request.REQUEST.get('ids')
        if not ids:
            return {'success': False, 'msg': 'Empty ids'}
        ids_lst = map(int, ids.split(','))
        if len(ids_lst) != 3:
            return {'success': False, 'msg': 'Ids len != 3'}
        desk_cards_lst = game.desk_cards_list
        if not all(card_id in desk_cards_lst for card_id in ids_lst):
            return {'success': False, 'msg': 'Not all card were on desk'}
        cards = [Card(id=card_id) for card_id in ids_lst]

        def is_set_wrapper(*args):
            if constants.CANCEL_SET_CHECK:
                return True
            else:
                return is_set(*args)
        if not is_set_wrapper(*cards):
            gs.state = GameSessionState.SET_PENALTY
            gs.failures += 1
            gs.save()
            return {'success': False, 'msg': 'Not SET!'}
        else:
            gs.state = GameSessionState.NORMAL
            gs.sets_found += 1
            gs.save()
            # Remove cards from desc list and replace with new, if any
            game.replace_cards(*ids_lst)
            result = {'success': True,
                      'msg': 'SET!',
                      'sets_found': gs.sets_found}
            return add_stat(gs, result)
    else:
        gs.state = GameSessionState.SET_PENALTY
        gs.failures += 1
        gs.save()
        return add_stat(gs, {'success': False, 'msg': 'Not in time!'})


@update_cache
def leave_game(request, game_id):
    gs = get_object_or_404(request.user.gamesession_set, game=game_id, left=False)
    gs.state = GameSessionState.LEFT
    gs.left = True
    gs.save()
    gs.game.finished = True
    gs.game.save()
    return redirect('/')
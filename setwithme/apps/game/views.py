# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from annoying.decorators import ajax_request, render_to

from game.models import Game, GameSession, GameSessionState, ClientConnectionState, get_uid
from game.utils import Card, is_set
from users.models import WaitingUser
from game import constants
from chat.models import ChatMessage


@render_to('game/game_screen.html')
def game_screen(request, game_id):
    return {'game_id': game_id}


@ajax_request
def start_game(request):
    user = request.user
    qs = GameSession.objects.\
        filter(user=user, game__finished=False).exclude(client_state=ClientConnectionState.LOST)
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
        return {'status': 'polling',
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
    GameSession.objects.get(game=game, user=request.user).update()
    chat_qs = ChatMessage.objects.filter(room=game)
    ts = request.REQUEST.get('ts', '')
    if ts:
        chat_qs = chat_qs.filter(timestamp__gte=float(ts))
    else:
        chat_qs = chat_qs.all()[0:10]
    users = [gs.serialize(request.user.id) for gs in \
        game.gamesession_set.all()]
    desc_cards = game.desk_cards_list
    desc_cards.extend(game.pop_cards(quantity=constants.CARDS_ON_DESK - len(desc_cards)))
    rem_cards_cnt = len(game.rem_cards_list)
    return {'users': users,
            'cards': [{'id': card_id,
                       'class': Card(id=card_id).as_text()} \
                        for card_id in desc_cards],
            'cards_left': rem_cards_cnt,
            'game': {
                'is_finished': game.is_finished(),
                'leader': game.leader},
            'chat': [cm.get_serialized(request.user) for cm in chat_qs]}


@ajax_request
def put_set_mark(request, game_id):
    game = Game.objects.get(id=game_id)
    if not game.gamesession_set.\
            filter(state=GameSessionState.SET_PRESSED).\
            count():
        gs = game.gamesession_set.get(user=request.user)
        gs.press_set()
        for g in game.gamesession_set.exclude(user=request.user).all():
            g.state = GameSessionState.NORMAL
            g.save()
        return {'success': True}
    return {'success': False}


@ajax_request
def check_set(request, game_id):
    game = Game.objects.get(id=game_id)
    gs = game.gamesession_set.get(user=request.user)

    # Update status to IDLE for other game sessions:
    for gs_other in game.gamesession_set.exclude(user=request.user).all():
        gs_other.state = GameSessionState.NORMAL
        gs_other.save()

    def add_stat(gs, data):
        data.update({'sets_found': gs.sets_found, 'failures': gs.failures, 'score': gs.score})
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
            # Remove cards from desc list
            game.drop_cards(*ids_lst)
            result = {'success': True, 'msg': 'SET!', 'sets_found': gs.sets_found}
            return add_stat(gs, result)
    else:
        gs.state = GameSessionState.SET_PENALTY
        gs.failures -= 1
        gs.save()
        return add_stat(gs, {'success': False, 'msg': 'Not in time!'})


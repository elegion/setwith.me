# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from annoying.decorators import ajax_request
from django.contrib.auth.models import User

from game.models import Game
from chat.models import ChatMessage


@login_required
@require_POST
@ajax_request
def put_message(request, game_id):
    message = request.POST.get('message', '')
    if not message:
        return {'success': False, 'msg': 'empty message'}
    room = Game.objects.get(id=game_id)
    ChatMessage.objects.create(
        sender=request.user,
        room=room,
        message=message)
    chat_qs = ChatMessage.objects.filter(
        room=room).all()[0:10]
    return {'success': True,
            'chat': [cm.get_serialized(request.user) for cm in chat_qs]}

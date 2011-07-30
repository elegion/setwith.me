# -*- coding: utf-8 -*-
import uuid
from annoying.decorators import render_to
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import login

@render_to('core/index.html')
def home(request):
    return {}


@render_to('core/lobby.html')
def lobby(request):
    return {
        'message': 'Set is designed by Marsha Falco in 1974 and published by Set Enterprises in 1991'
    }


def login(request, provider):
    if provider == 'facebook':
        _facebook_login(request)
    elif provider == 'anon':
        _anon_login(request)
    else:
        raise NotImplementedError('Provider %s login method not implemented' %
            provider)
    return redirect(home)


def _facebook_login(request):
    fb = request.facebook
    if fb and fb.uid and fb.graph:
        user, created = User.objects.get_or_create(username=fb.uid)
        if created:
            me = fb.graph.get_object('me')
            if me:
                if me.get('first_name'): user.first_name = me['first_name']
                if me.get('last_name'): user.last_name = me['last_name']
                if me.get('email'): user.email = me['email']
                user.save()
        return True
    return False


def _anon_login(request):
    user_uuid = unicode(uuid.uuid4().hex)[:30]
    user, created = User.objects.get_or_create(
        username=user_uuid,
        defaults={'first_name': 'Anon %s' % (user_uuid[:4],)})
    login(request, user)
    return True

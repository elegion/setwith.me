# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login,\
    logout as auth_logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


REDIRECT_AFTER_LOGIN = getattr(settings, 'REDIRECT_AFTER_LOGIN', '/lobby/')
REDIRECT_AFTER_LOGOUT = getattr(settings, 'REDIRECT_AFTER_LOGOUT', '/')


@require_POST
def logout(request):
    auth_logout(request)
    return redirect(REDIRECT_AFTER_LOGOUT)


@require_POST
def login(request, provider):
    if provider == 'anonymous':
        user = anonymous_login(request)
    elif provider == 'facebook':
        user = facebook_login(request)
    elif provider == 'vkontakte':
        user = vkontakte_login(request)
    else:
        raise NotImplementedError('Provider %s is not implemented' % provider)

    if user is not None:
        auth_login(request, user)
        return redirect(REDIRECT_AFTER_LOGIN)
    return redirect('/')


def anonymous_login(request):
    return authenticate()


def facebook_login(request):
    fb = request.facebook
    if fb and fb.uid and fb.graph:
        return authenticate(fb_uid=fb.uid, fb_graphtoken=fb.access_token)
    return None


def vkontakte_login(request):
    vk = request.vk
    if vk:
        return authenticate(vk_mid=vk.mid)
    return None

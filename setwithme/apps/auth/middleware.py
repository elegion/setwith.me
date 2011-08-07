# -*- coding: utf-8 -*-
import cgi
import hashlib
import time

from django.conf import settings
from django_facebook.middleware import FacebookMiddleware as FBMiddleware

from auth.utils import GraphAPI


class DjangoFacebook(object):
    """
    Simple accessor object for the Facebook user.
    Uses tweaked GraphAPI class
    """
    def __init__(self, user):
        self.user = user
        self.uid = user['uid']
        self.access_token = user['access_token']
        self.graph = GraphAPI(user['access_token'])


class DjangoVkontakte(object):
    """
    Simple accessor object for the Vkontakte user
    """
    def __init__(self, user):
        self.user = user
        self.mid = user['mid']


class FacebookMiddleware(FBMiddleware):
    """
    We don't need auth_login action at every request
    That's why we re-implement middleware
    """
    def process_request(self, request):
        fb_user = self.get_fb_user(request)
        request.facebook = DjangoFacebook(fb_user) if fb_user else None
        return None


class VkontakteMiddleware(object):

    api_key = getattr(settings, 'VK_APP_ID', '')
    api_secret = getattr(settings, 'VK_SECRET_KEY', '')

    def get_vk_user_from_cookie(self, cookies):
        cookie_name = 'vk_app_%s' % self.api_key
        cookie = cookies.get(cookie_name)
        if cookie is None:
            return None
        args = dict(
                (k, v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items()
        )
        payload = "".join(k + "=" + args[k] for k in sorted(args.keys())
                          if k != "sig")
        sig = hashlib.md5(payload + self.api_secret).hexdigest()
        expires = int(args["expire"])
        if sig == args.get("sig") and (expires == 0 or time.time() < expires):
            return args
        else:
            return None

    def get_vk_user(self, request):
        return self.get_vk_user_from_cookie(request.COOKIES)

    def process_request(self, request):
        vk_user = self.get_vk_user(request)
        request.vk = DjangoVkontakte(vk_user) if vk_user else None
        return None

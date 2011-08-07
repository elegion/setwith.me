# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
import vkontakte
from unidecode import unidecode

from auth.utils import GraphAPI
from users.models import UserProfile


class AnonymousBackend(ModelBackend):
    """
    Creates anonymous user
    """
    def authenticate(self, *args, **kwargs):
        user_uuid = kwargs.get('user_uuid') or unicode(uuid.uuid4().hex)[:30]
        user, created = User.objects.get_or_create(
            username=user_uuid,
            defaults={'first_name': 'Anon %s' % (user_uuid[:4],)}
        )
        return user


class FacebookBackend(ModelBackend):
    """
    Authenticate a facebook user and
    autopopulate facebook data into the users profile
    """
    def authenticate(self, fb_uid=None, fb_graphtoken=None):
        """
        If we receive a facebook uid then the cookie has already been validated
        """
        if fb_uid and fb_graphtoken:
            user, created = User.objects.get_or_create(username=fb_uid)
            profile = UserProfile.objects.get_or_create(user=user)[0]
            #if created:
            if True:
                # It would be nice to replace this with an asynchronous request
                graph = GraphAPI(fb_graphtoken)
                me = graph.get_object('me')
                if me:
                    print me
                    if me.get('first_name'): user.first_name = me['first_name']
                    if me.get('last_name'): user.last_name = me['last_name']
                    if me.get('email'): user.email = me['email']
                    pic = GraphAPI().get_connections('%s' % fb_uid,
                                                     'picture',
                                                     type='square')
                    profile.user_pic = pic.get('url', '')
                    profile.save()
                    user.save()
            return user
        return None


class VkontakteBackend(ModelBackend):
    """
    Authenticates a vkontakte user
    """
    api_key = getattr(settings, 'VK_APP_ID', '')
    api_secret = getattr(settings, 'VK_SECRET_KEY', '')

    def authenticate(self, vk_mid=None, *args, **kwargs):
        if vk_mid:
            user, created = User.objects.\
                    get_or_create(username='vk_%s' % vk_mid)
            profile = UserProfile.objects.get_or_create(user=user)[0]
            if True:
                vk = vkontakte.API(self.api_key, self.api_secret)
                vk_user = vk.getProfiles(uid=vk_mid,
                                         fields='first_name,last_name,photo')
                vk_user = vk_user[0]
                if vk_user:
                    user.first_name = unidecode(vk_user.get('first_name', ''))
                    user.last_name = unidecode(vk_user.get('last_name', ''))
                    profile.user_pic = vk_user.get('photo', '')
                    profile.save()
                    user.save()
            return user
        return None

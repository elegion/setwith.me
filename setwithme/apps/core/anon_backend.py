# -*- coding: utf-8 -*-
import uuid
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class AnonymousBackend(ModelBackend):
    """ Create anon user. """
    def authenticate(self, *args, **kwargs):
        user_uuid = kwargs.get('user_uuid', '')
        user_uuid = user_uuid or unicode(uuid.uuid4().hex)[:30]
        user, created = User.objects.get_or_create(
            username=user_uuid, defaults={'first_name': 'Anon_%s' % (user_uuid[:4],)})
        return user

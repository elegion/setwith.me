# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth.models import User


class UserOnlineMiddleware(object):
    def process_request(self, request):
        if request.is_ajax():
            return None
        if request.user and request.user.is_authenticated():
            user = User.objects.get(id=request.user.id)
            user.last_login = datetime.datetime.now()
            user.save()
        return None

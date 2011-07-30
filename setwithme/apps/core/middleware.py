# -*- coding: utf-8 -*-
import datetime
from django.contrib import auth


class CookieAuthMiddleware(object):

    def process_request(self, request):
        if not request.user.is_anonymous():
            return None
        user_uuid = request.session.get('anon_uuid', '')
        user = auth.authenticate(
            user_uuid=user_uuid)
        if user:
            request.session['anon_uuid'] = user.username
            user.last_login = datetime.datetime.now()
            user.save()
            request.user = user

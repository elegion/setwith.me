# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User

class CsrfFixMiddleware(object):
    def process_view(self, request, view_func, callback_args, callback_kwargs):
        request.META["CSRF_COOKIE_USED"] = True
        return None


class UserOnlineMiddleware(object):
    def process_request(self, request):
        if request.is_ajax():
            return None
        if request.user and request.user.is_authenticated():
            user = User.objects.get(id=request.user.id)
            user.last_login = datetime.datetime.now()
            user.save()
        return None

# -*- coding: utf-8 -*-
class CsrfFixMiddleware(object):
    def process_view(self, request, view_func, callback_args, callback_kwargs):
        request.META["CSRF_COOKIE_USED"] = True
        return None

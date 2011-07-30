# -*- coding: utf-8 -*-
from annoying.decorators import JsonResponse
from django.shortcuts import render_to_response


def home(request):
    return render_to_response("core/index.html", {})


def stub(request):
    return JsonResponse({
        'success': True
    })

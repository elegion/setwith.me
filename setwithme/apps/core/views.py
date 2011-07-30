# -*- coding: utf-8 -*-
from annoying.decorators import render_to


@render_to('core/index.html')
def home(request):
    return {}


@render_to('core/lobby.html')
def lobby(request):
    return {
        'message': 'Set is designed by Marsha Falco in 1974 and published by Set Enterprises in 1991'
    }

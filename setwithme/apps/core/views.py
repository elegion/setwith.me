# -*- coding: utf-8 -*-
from annoying.decorators import render_to


@render_to('core/index.html')
def home(request):
    return {}

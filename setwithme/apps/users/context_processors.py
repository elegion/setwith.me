# -*- coding: utf-8 -*-
from django.conf import settings

from users.models import UserProfile


def user_profile(request):
    profile = None
    if hasattr(request, 'user'):
        user = request.user
        if user.is_authenticated():
            profile = UserProfile.objects.get_or_create(user=user)[0]
            if not profile.user_pic:
                profile.user_pic = settings.DEFAULT_PROFILE_PIC
    return {
        'user_profile': profile or {'user_pic': settings.DEFAULT_PROFILE_PIC}
    }

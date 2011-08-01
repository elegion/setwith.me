# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class WaitingUser(models.Model):

    user = models.ForeignKey(User)
    last_poll = models.DateTimeField(default=datetime.datetime.now)

    def update(self):
        self.last_poll = datetime.datetime.now()
        self.save()
        return self

    def serialize(self):
        return get_user_json(self.user)

    def __unicode__(self):
        return self.user.username


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    user_pic = models.CharField(max_length=300, default='')
    games_total = models.PositiveIntegerField(default=0)
    games_win = models.PositiveIntegerField(default=0)
    games_loss = models.PositiveIntegerField(default=0)

    def get_user_pic(self):
        return self.user_pic if self.user_pic \
            else settings.DEFAULT_PROFILE_PIC


def get_user_json(user):
    profile = UserProfile.objects.get_or_create(user=user)[0]
    pic = profile.get_user_pic()
    if user.first_name or user.last_name:
        name = u"%s %s" % (user.first_name, user.last_name)
    else:
        name = user.username
    return {'id': user.id,
            'username': user.username,
            'name': name,
            'pic': pic}

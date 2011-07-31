# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User

class WaitingUser(models.Model):

    user = models.ForeignKey(User)
    last_poll = models.DateTimeField(default=datetime.datetime.now)
    confirmed = models.BooleanField(default=False)

    def update(self):
        self.last_poll = datetime.datetime.now()
        self.save()
        return self

    def confirm(self):
        self.confirmed = True
        self.save()

    def serialize(self):
        return {'username': self.user.username,
                'confirmed': self.confirmed}

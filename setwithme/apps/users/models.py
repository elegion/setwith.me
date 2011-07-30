# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    
    user = models.OneToOneField(User, db_index=True)


class WaitingUser(models.Model):

    user = models.ForeignKey(User)
    last_poll = models.DateTimeField(default=datetime.datetime.now)

    def update(self):
        self.last_poll = datetime.datetime.now()
        self.save()
        return self

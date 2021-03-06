# -*- coding: utf-8 -*-
import datetime
import time

from django.contrib.auth.models import User
from django.db import models

from game.models import Game


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, )
    room = models.ForeignKey(Game)
    message = models.TextField()
    timestamp = models.FloatField(default=time.time)
    created = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ['-timestamp']

    def get_serialized(self, current_user):
        return {
            'sender': 'Me' if self.sender == current_user else self.sender.first_name,
            'room': self.room_id,
            'timestamp': self.timestamp,
            'message': self.message,
            'created': self.created.strftime("%Y-%m-%d %H-%M-%S")}

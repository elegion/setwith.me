# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    
    user = models.OneToOneField(User, db_index=True)

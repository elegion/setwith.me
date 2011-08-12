# -*- coding: utf-8 -*-
import os
import sys

WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP_DIR = os.path.dirname(WORK_DIR)

ALLDIRS = [
        '/venvs/setwithme/lib/python2.7/site-packages',
        WORK_DIR,
        UP_DIR,
]

import site

# Remember original sys.path.
prev_sys_path = list(sys.path)

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

os.environ['DJANGO_SETTINGS_MODULE'] = 'setwithme.settings'
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

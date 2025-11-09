# IMPORTANT: Monkey patch eventlet BEFORE any other imports
import eventlet

eventlet.monkey_patch()

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.celery_app import celery_app
import os, sys

sys.path.append('/var/www/html/nuri')
os.environ['DJANGO_SETTINGS_MODULE'] = 'nuri.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()


import os, sys
import django.core.handlers.wsgi
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = os.path.basename(os.path.dirname(__file__)) + '.settings'
application = django.core.handlers.wsgi.WSGIHandler()
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__))))
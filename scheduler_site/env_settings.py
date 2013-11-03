#./manage.py dumpdata --e contenttypes --e auth.permission --e sessions.session --format=json > scheduler/fixtures/initial_data.json
# FIXTURE_DIRS = (
#    'YOUR_PATH/star/scheduler/fixtures/initial_data.json',
# )
import sys, os

if 'Linux' in sys.platform:
    path = '/home/chuck/Dropbox/school/soen341/star/schedule.db'
else:
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schedule.db')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': path,  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

EXTRA_APPS = ()
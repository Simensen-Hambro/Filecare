import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "filecare.settings")

application = get_wsgi_application()

try:
    import uwsgidecorators
    

    @uwsgidecorators.timer(7200)
    def index_root_directory(num):
        """Index root directory every 2 hours"""
        call_command('traverse', processes=1)


    @uwsgidecorators.timer(7200)
    def prune_expired_shares(num):
        """Prune expired Shares every 2 hours"""
        call_command('pruneexpired', processes=1)

except ImportError:
    print("uwsgidecorators not found. Cron and timers are disabled")

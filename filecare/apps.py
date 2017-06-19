from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'filecare'

    def ready(self):
        from . import signals
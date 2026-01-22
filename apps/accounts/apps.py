from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        from django.contrib.sessions.models import Session
        Session.objects.all().delete()

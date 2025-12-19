from django.contrib.sessions.models import Session

def clear_all_sessions():
    Session.objects.all().delete()

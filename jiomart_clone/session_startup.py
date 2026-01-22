def clear_all_sessions():
    from django.contrib.sessions.models import Session
    Session.objects.all().delete()

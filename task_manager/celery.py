import os

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from tasks.models import Task

from celery import Celery
from celery.decorators import periodic_task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
app = Celery("task_manager")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# Periodic Task
@periodic_task(run_every=timedelta(seconds=30))
def send_email_reminder():
    print("Starting to process Emails")
    for user in User.objects.all():
        pending_qs = Task.objects.filter(user=user, complete=False, deleted=False)
        email_content = f"You have {pending_qs.count()} pending tasks."
        send_mail("Pending Task from Task Manager", email_content, "task@taskmanager.org", [user.email])
        print(f"Completed Processing User {user.id}")


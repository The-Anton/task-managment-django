from datetime import datetime, timedelta, timezone

from celery.decorators import periodic_task
from celery.schedules import crontab
from django.contrib.auth.models import User
from django.core.mail import send_mail
from task_manager.celery import app

from tasks.models import EmailScheduler, Task


def send_mail_client(user):
    pending_task_count = Task.objects.filter(user=user, status="PENDING", deleted=False).count()
    completed_task_count = Task.objects.filter(user=user, status="COMPLETED", deleted=False).count()
    canceled_task_count = Task.objects.filter(user=user, status="CANCELLED", deleted=False).count()
    inprogress_task_count = Task.objects.filter(user=user, status="IN_PROGRESS", deleted=False).count()

    content = f" Your task report: \n\n {pending_task_count} Pending Task \n {completed_task_count} Completed Task \n {canceled_task_count} Canceled Task \n {inprogress_task_count} Inprogress Task"

    send_mail("Your Task Report for the day", content, "tasks@taskmanager.org", [user.email])

    print(f"{user} email sent!!")
    print(content)


@periodic_task(run_every=timedelta(seconds=60))
def send_email_reminder():
    print("Starting to process Emails")
    mail_configs = EmailScheduler.objects.filter( mail_time__lte=datetime.now(timezone.utc), last_mailed__lt=datetime.now(timezone.utc).date()).select_for_update()

    for mail_config in mail_configs:
       user = User.objects.get(id=mail_config.user.id)
       send_mail_client(user)
       mail_config.last_mailed = datetime.now(timezone.utc)
       mail_config.save()



from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    user = models.ForeignKey(User , on_delete=models.CASCADE , null=True,blank=True)

    def __str__(self):
        return self.title

class History(models.Model):
    old_status = models.CharField(max_length=100)
    new_status = models.CharField(max_length=100)
    change_time = models.DateTimeField(auto_now=True)
    task = models.ForeignKey(Task,on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class EmailScheduler(models.Model):
    mail_time = models.TimeField(default=datetime.now().time())
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    last_mailed = models.DateTimeField(default=datetime.now(timezone.utc), null=True, blank=True)
    
    def __str__(self):
        return f"{self.mail_time}"

@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    if not EmailScheduler.objects.filter(user=kwargs["instance"]).exists():
        new_schedule = EmailScheduler(user=kwargs["instance"])
        new_schedule.save()
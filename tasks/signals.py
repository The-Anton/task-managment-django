from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from tasks.models import Task, TaskEmail, TaskHistory, User


@receiver(post_save, sender=User)
def mailSchedule(sender, instance, created, **kwargs):
    if created:
        TaskEmail.objects.create(user=instance)


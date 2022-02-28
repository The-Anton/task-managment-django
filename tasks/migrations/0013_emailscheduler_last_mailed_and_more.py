# Generated by Django 4.0.1 on 2022-02-28 11:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_alter_emailscheduler_mail_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailscheduler',
            name='last_mailed',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 2, 28, 11, 54, 1, 204079, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='emailscheduler',
            name='mail_time',
            field=models.TimeField(default=datetime.time(11, 54, 1, 204018)),
        ),
    ]
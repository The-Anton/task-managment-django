# Generated by Django 4.0.1 on 2022-03-05 13:28

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_emailscheduler_last_mailed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailscheduler',
            name='last_mailed',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 3, 5, 13, 28, 26, 475876, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='emailscheduler',
            name='mail_time',
            field=models.TimeField(default=datetime.time(13, 28, 26, 475816)),
        ),
    ]

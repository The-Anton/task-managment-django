# Generated by Django 4.0.1 on 2022-02-25 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_emailscheduler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailscheduler',
            name='mail_time',
            field=models.TimeField(),
        ),
    ]

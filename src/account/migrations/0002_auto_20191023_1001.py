# Generated by Django 2.1.5 on 2019-10-23 10:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decisions',
            name='application_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 23, 10, 0, 57, 139447)),
        ),
        migrations.AlterField(
            model_name='student',
            name='plan_valid_till',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 23, 10, 0, 57, 120603)),
        ),
    ]

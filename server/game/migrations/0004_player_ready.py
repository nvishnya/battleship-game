# Generated by Django 3.1.2 on 2020-10-27 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20201023_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='ready',
            field=models.BooleanField(default=False),
        ),
    ]

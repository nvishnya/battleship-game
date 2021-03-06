# Generated by Django 3.1.2 on 2020-10-27 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_player_ready'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='ready',
            new_name='is_ready',
        ),
        migrations.AddField(
            model_name='player',
            name='is_busy',
            field=models.BooleanField(default=False),
        ),
    ]

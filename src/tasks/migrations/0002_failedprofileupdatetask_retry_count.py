# Generated by Django 3.2.6 on 2022-04-15 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='failedprofileupdatetask',
            name='retry_count',
            field=models.IntegerField(default=0),
        ),
    ]

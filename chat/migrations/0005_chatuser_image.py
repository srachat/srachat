# Generated by Django 3.0.3 on 2020-04-05 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_room_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatuser',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-02-19 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_usermodel_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
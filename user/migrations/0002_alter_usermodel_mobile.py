# Generated by Django 5.0.1 on 2024-02-06 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='mobile',
            field=models.IntegerField(),
        ),
    ]

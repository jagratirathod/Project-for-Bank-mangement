# Generated by Django 4.2.1 on 2023-05-09 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='account_number',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
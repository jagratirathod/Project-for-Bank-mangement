# Generated by Django 4.2.1 on 2023-05-08 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transction',
            name='balance_after_transaction',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]

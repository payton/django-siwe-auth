# Generated by Django 4.0.5 on 2022-06-10 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siwe_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='datetime created'),
        ),
    ]
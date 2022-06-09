# Generated by Django 4.0.5 on 2022-06-09 00:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('siwe_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notepad',
            fields=[
                ('wallet', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SharedNotepad',
            fields=[
                ('name', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('value', models.TextField()),
            ],
        ),
    ]

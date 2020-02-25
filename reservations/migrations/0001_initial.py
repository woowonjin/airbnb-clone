# Generated by Django 2.2.5 on 2020-02-17 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0004_auto_20200215_2022'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='pending', max_length=12)),
                ('check_in', models.DateField(default=django.utils.timezone.now)),
                ('check_out', models.DateField(default=django.utils.timezone.now)),
                ('guest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rooms.Room')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

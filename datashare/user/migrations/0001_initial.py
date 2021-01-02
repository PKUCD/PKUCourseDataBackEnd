# Generated by Django 3.1.4 on 2020-12-26 05:15

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('avatar', models.CharField(blank=True, max_length=128)),
                ('pku_mail', models.EmailField(max_length=254, unique=True)),
                ('sha256_password', models.CharField(blank=True, max_length=64)),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pku_mail', models.EmailField(max_length=254, unique=True)),
                ('verification_code', models.CharField(max_length=6)),
                ('update_date', models.DateTimeField()),
                ('veri_type', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': '验证码',
                'verbose_name_plural': '验证码',
            },
        ),
    ]

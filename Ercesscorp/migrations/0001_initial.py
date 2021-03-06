# Generated by Django 2.1.7 on 2019-05-11 08:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogData',
            fields=[
                ('blog_id', models.AutoField(primary_key=True, serialize=False)),
                ('author', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.FileField(default='images/business-events-cover-1.jpg', upload_to='images')),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ContactData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=70)),
                ('mobile', models.BigIntegerField()),
                ('purpose', models.CharField(max_length=20)),
                ('comment', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(default='blank', max_length=10)),
                ('location', models.CharField(default='blank', max_length=30)),
                ('submitted', models.IntegerField(default=0)),
                ('how_u_know', models.CharField(default='other', max_length=100)),
                ('verify', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='reg', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRegistrationToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email_token', models.CharField(default='', max_length=250)),
                ('user_email_token_created_on', models.DateTimeField(blank=True, null=True)),
                ('user_password_token', models.CharField(default='', max_length=250)),
                ('user_email', models.CharField(default='', max_length=250)),
                ('user_password_token_created_on', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_userid', models.TextField(blank=True, null=True)),
                ('md5', models.CharField(max_length=300)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('user', models.CharField(max_length=40)),
                ('profile_pic', models.TextField()),
                ('gender', models.CharField(max_length=8)),
                ('location', models.CharField(max_length=25)),
                ('mobile', models.CharField(max_length=11)),
                ('password', models.CharField(blank=True, max_length=300, null=True)),
                ('mobile_verified', models.IntegerField(default=0)),
                ('status', models.CharField(default='pending', max_length=8)),
                ('first_time', models.CharField(max_length=10)),
                ('organization_name', models.CharField(max_length=200)),
                ('organization_location', models.TextField()),
            ],
        ),
    ]

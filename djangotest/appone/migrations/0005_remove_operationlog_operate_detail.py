# Generated by Django 2.2.5 on 2021-09-08 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appone', '0004_operationlog_wife'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operationlog',
            name='operate_detail',
        ),
    ]

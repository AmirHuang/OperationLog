# Generated by Django 2.2.6 on 2021-09-08 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appone', '0007_auto_20210908_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationlog',
            name='operate_detail',
            field=models.TextField(default=[], verbose_name='操作详情'),
        ),
    ]
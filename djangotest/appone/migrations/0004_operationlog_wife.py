# Generated by Django 2.2.5 on 2021-09-08 08:14

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('appone', '0003_card_carddetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.CharField(db_index=True, default='', max_length=64, verbose_name='操作账号')),
                ('operate_type', models.CharField(choices=[('add', '新增'), ('modify', '修改'), ('exec', '执行'), ('delete', '删除')], max_length=128, verbose_name='操作类型')),
                ('created_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='添加时间')),
                ('operate_obj', models.CharField(default='', max_length=64, verbose_name='操作对象')),
                ('operate_summary', models.TextField(default='', max_length=500, verbose_name='操作概要')),
                ('operate_detail', jsonfield.fields.JSONField(default=[], verbose_name='操作详情')),
            ],
            options={
                'verbose_name': '使用记录',
            },
        ),
        migrations.CreateModel(
            name='Wife',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('created_by', models.CharField(default='', max_length=100, verbose_name='创建人')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('updated_by', models.CharField(default='', max_length=100, verbose_name='更新人')),
                ('name', models.CharField(max_length=255, verbose_name='名称')),
                ('high', models.IntegerField(verbose_name='身高')),
                ('age', models.IntegerField(verbose_name='年龄')),
                ('weight', models.IntegerField(verbose_name='体重')),
            ],
            options={
                'verbose_name': '娘们个人资料',
                'verbose_name_plural': '娘们',
            },
        ),
    ]

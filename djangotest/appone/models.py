import copy
from django.db import models
from django.db.models.query import QuerySet
from celery_tasks.appone.tasks import operate_log_task
from django.db import (connections, transaction)
from django.db.models.functions import Cast
from django.db.models.expressions import Case, Expression, Value, When


def get_current_request():
    # 获取当前登录用户,可通过中间件+threadlocal+偏函数实现
    return 'xxx'


class MyQuerySet(QuerySet):

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False, is_log=False):
        super(MyQuerySet, self).bulk_create(objs, batch_size=None, ignore_conflicts=False)
        operate_user = get_current_request()
        if is_log:
            for obj in objs:
                operate_log_task.delay("log_created", sender=type(obj), new_obj=obj, operate_user=operate_user)

    def bulk_update(self, objs, fields, batch_size=None, is_log=False, **kwargs):
        """
        Update the given fields in each of the given objects in the database.
        """
        if batch_size is not None and batch_size < 0:
            raise ValueError('Batch size must be a positive integer.')
        if not fields:
            raise ValueError('Field names must be given to bulk_update().')
        objs = tuple(objs)
        if any(obj.pk is None for obj in objs):
            raise ValueError('All bulk_update() objects must have a primary key set.')
        fields = [self.model._meta.get_field(name) for name in fields]
        if any(not f.concrete or f.many_to_many for f in fields):
            raise ValueError('bulk_update() can only be used with concrete fields.')
        if any(f.primary_key for f in fields):
            raise ValueError('bulk_update() cannot be used with primary key fields.')
        if not objs:
            return
        # PK is used twice in the resulting update query, once in the filter
        # and once in the WHEN. Each field will also have one CAST.
        max_batch_size = connections[self.db].ops.bulk_batch_size(['pk', 'pk'] + fields, objs)
        batch_size = min(batch_size, max_batch_size) if batch_size else max_batch_size
        requires_casting = connections[self.db].features.requires_casted_case_in_updates
        batches = (objs[i:i + batch_size] for i in range(0, len(objs), batch_size))
        updates = []
        for batch_objs in batches:
            update_kwargs = {}
            for field in fields:
                when_statements = []
                for obj in batch_objs:
                    attr = getattr(obj, field.attname)
                    if not isinstance(attr, Expression):
                        attr = Value(attr, output_field=field)
                    when_statements.append(When(pk=obj.pk, then=attr))
                case_statement = Case(*when_statements, output_field=field)
                if requires_casting:
                    case_statement = Cast(case_statement, output_field=field)
                update_kwargs[field.attname] = case_statement
            updates.append(([obj.pk for obj in batch_objs], update_kwargs))

        with transaction.atomic(using=self.db, savepoint=False):
            for pks, update_kwargs in updates:
                if is_log:
                    qs = self.filter(pk__in=pks)
                    old_objs = [copy.deepcopy(item) for item in qs]
                    kwargs["updated_by"] = kwargs.get("updated_by") or get_current_request()
                    qs.update(**update_kwargs)
                    operate_user = get_current_request()
                    for index, obj in enumerate(objs):
                        operate_log_task.delay(
                            "log_update", sender=type(obj), new_obj=obj, old_obj=old_objs[index],
                            operate_user=operate_user
                        )
                else:
                    self.filter(pk__in=pks).update(**update_kwargs)

    def update(self, is_log=False, **kwargs):
        old_objs = [copy.deepcopy(item) for item in self]
        kwargs["updated_by"] = kwargs.get("updated_by") or get_current_request()
        super().update(**kwargs)
        if is_log:
            operate_user = get_current_request()
            for index, obj in enumerate(self):
                operate_log_task.delay(
                    "log_update", sender=type(obj), new_obj=obj, old_obj=old_objs[index], operate_user=operate_user
                )

    def create(self, is_log=False, **kwargs):
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True, using=self.db, is_log=is_log)
        return obj

    def delete(self, is_log=False):
        old_objs = [copy.deepcopy(item) for item in self]
        count, obj_dict = super().delete()
        if is_log:
            operate_user = get_current_request()
            for index, obj in enumerate(old_objs):
                operate_log_task.delay("log_delete", sender=type(obj), delete_obj=obj, operate_user=operate_user)
        return count, obj_dict

    # def bulk_update(self, objs, fields, is_log=False, old_objs=None, batch_size=None):
    #     '''
    #     :param is_log: 记录更新日志
    #     :param kwargs: 需要深度拷贝更新之前的数据,并传过来.
    #             比如: bulk_update(self, objs, fields, batch_size=None, is_log=True, old_objs=old_objs)
    #     :示例:
    #         a_dict = {1: {'id': 1, "name": '额', "high": 1, "age": 2, "weight": 3},
    #           2: {'id': 2, "name": '他', "high": 1, "age": 2, "weight": 3},
    #           3: {'id': 3, "name": 'y人', "high": 1, "age": 2, "weight": 3}}
    #         ids = [1, 2, 3]
    #         wifes = Wife.objects.filter(id__in=ids)
    #         old_wifes = copy.deepcopy(wifes)
    #         update_objs = []
    #         for wife in wifes:
    #             wife.name = a_dict[wife.id]['name']
    #             update_objs.append(wife)
    #         Wife.objects.bulk_update(update_objs, ['name'], is_log=True, old_objs=old_wifes)
    #
    #     '''
    #
    #     super().bulk_update(objs, fields, batch_size=None)
    #
    #     if is_log:
    #         if not old_objs:
    #             raise Exception("缺少old_objs参数")
    #         operate_user = get_current_request()
    #         for index, obj in enumerate(objs):
    #             operate_log_task.delay(
    #                 "log_update", sender=type(obj), new_obj=obj, old_obj=old_objs[index], operate_user=operate_user
    #             )


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    created_by = models.CharField(verbose_name="创建人", max_length=100, default="")
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    updated_by = models.CharField(verbose_name="更新人", default="", max_length=100)
    objects = MyQuerySet().as_manager()

    class Meta:
        abstract = True

    def save(self, is_log=False, old_obj=None, *args, **kwargs):
        old_obj = copy.deepcopy(type(self)).objects.filter(id=self.id).first() if self.id else None
        operate_user = get_current_request()
        if old_obj:
            self.updated_by = operate_user
        else:
            self.created_by = operate_user
        super().save(*args, **kwargs)
        if is_log:
            if old_obj:
                operate_log_task.delay(
                    "log_update", sender=type(self), new_obj=self, old_obj=old_obj, operate_user=operate_user
                )
            else:
                operate_log_task.delay("log_created", sender=type(self), new_obj=self, operate_user=operate_user)

    def delete(self, is_log=False, using=None):
        super().delete(using)
        if is_log:
            operate_user = get_current_request()
            operate_log_task.delay("log_delete", sender=type(self), delete_obj=self, operate_user=operate_user)


# 操作日志
class OperationLog(models.Model):
    class Meta:
        verbose_name = "使用记录"

    ADD = "add"
    MODIFY = "modify"
    EXEC = "exec"
    DELETE = "delete"
    OPERATE_TYPE_CHOICES = ((ADD, "新增"), (MODIFY, "修改"), (EXEC, "执行"), (DELETE, "删除"))
    operator = models.CharField("操作账号", max_length=64, default="", db_index=True)
    operate_type = models.CharField("操作类型", choices=OPERATE_TYPE_CHOICES, max_length=128)
    created_time = models.DateTimeField("添加时间", auto_now_add=True, db_index=True)
    operate_obj = models.CharField("操作对象", max_length=64, default="")
    operate_summary = models.TextField("操作概要", max_length=500, default="")
    operate_detail = models.TextField("操作详情", default=[])


class Wife(BaseModel):
    name = models.CharField('名称', max_length=255)
    high = models.IntegerField('身高')
    age = models.IntegerField('年龄')
    weight = models.IntegerField('体重')

    class Meta:
        verbose_name_plural = '娘们'
        verbose_name = "娘们个人资料"


class Publisher(models.Model):
    name = models.CharField(max_length=32)


# Create your models 浏览here.
class Book(models.Model):
    title = models.CharField(max_length=32)
    pub = models.ForeignKey('Publisher', on_delete=models.CASCADE)  # 与出版社之间建立多对一外键


class Author(models.Model):
    name = models.CharField(max_length=32)
    books = models.ManyToManyField('Book')  # 描述多对多的关系  不生成字段  生成关系表


class Person(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through='Membership')

    def __str__(self):
        return self.name


class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)


class Card(models.Model):
    '''银行卡 基本信息'''
    card_id = models.CharField(max_length=30, verbose_name="卡号", default="")
    card_user = models.CharField(max_length=10, verbose_name="姓名", default="")
    add_time = models.DateField(auto_now=True, verbose_name="添加时间")

    class Meta:
        verbose_name_plural = '银行卡账户'
        verbose_name = "银行卡账户_基本信息"

    def __str__(self):
        return self.card_id


class CardDetail(models.Model):
    '''银行卡 详情信息'''
    card = models.OneToOneField(Card,
                                on_delete=models.CASCADE,
                                verbose_name="卡号"
                                )
    tel = models.CharField(max_length=30, verbose_name="电话", default="")
    mail = models.CharField(max_length=30, verbose_name="邮箱", default="")
    city = models.CharField(max_length=10, verbose_name="城市", default="")
    address = models.CharField(max_length=30, verbose_name="详细地址", default="")

    class Meta:
        verbose_name_plural = '个人资料'
        verbose_name = "账户_个人资料"

    def __str__(self):
        return self.card.card_user

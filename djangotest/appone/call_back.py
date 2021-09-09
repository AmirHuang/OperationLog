# -*- encoding: utf-8 -*-
from django.db.models import Model

from appone import models


class OperationLogFunc:
    def __init__(self):
        self.ignore_module = (models.OperationLog,)
        self.ignore_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def log_created(self, sender, **kwargs):
        if sender in self.ignore_module:
            return
        instance = kwargs.get("new_obj", None)
        operate_user = kwargs.get("operate_user", None)
        field_list = sender._meta.fields
        operate_detail = []
        for i in field_list[1:]:
            if i.name in self.ignore_fields:
                continue
            # help_text 这个属性 可以做为特殊的标记用途
            if i.help_text:
                continue
            if isinstance(getattr(instance, i.name), Model):
                operate_detail.append({"name": i.verbose_name, "value": getattr(instance, i.name).__str__()})
            else:
                operate_detail.append({"name": i.verbose_name, "value": getattr(instance, i.name)})
        models.OperationLog.objects.create(
            operator=operate_user,
            operate_type=models.OperationLog.ADD,
            operate_detail=operate_detail,
            operate_obj=instance._meta.verbose_name,
            operate_summary="新增" + instance._meta.verbose_name + "[" + str(instance) + "]",
        )

    def log_delete(self, sender, **kwargs):
        if sender in self.ignore_module:
            return
        instance = kwargs.get("delete_obj", None)
        operate_user = kwargs.get("operate_user", None)
        field_list = sender._meta.fields
        operate_detail = []
        for i in field_list[1:]:
            if i.name in self.ignore_fields:
                continue
            if i.help_text:
                continue
            if isinstance(getattr(instance, i.name), Model):
                operate_detail.append({"name": i.verbose_name, "value": getattr(instance, i.name).__str__()})
            else:
                operate_detail.append({"name": i.verbose_name, "value": getattr(instance, i.name)})
        models.OperationLog.objects.create(
            operator=operate_user,
            operate_type=models.OperationLog.DELETE,
            operate_detail=operate_detail,
            operate_obj=instance._meta.verbose_name,
            operate_summary="删除" + instance._meta.verbose_name + str(instance),
        )

    def log_update(self, sender, **kwargs):
        if sender in self.ignore_module:
            return
        new_obj = kwargs.get("new_obj", None)
        old_obj = kwargs.get("old_obj", None)
        operate_user = kwargs.get("operate_user", None)
        field_list = sender._meta.fields
        operate_detail = []
        for i in field_list[1:]:
            if i.name in self.ignore_fields:
                continue
            if i.help_text:
                continue
            new_value = getattr(new_obj, i.name)
            old_value = getattr(old_obj, i.name)
            if isinstance(new_value, Model) and isinstance(old_value, Model):
                if new_value.__str__() != old_value.__str__():
                    value = "[{}] ==> [{}]".format(old_value.__str__(), new_value.__str__())
                    operate_detail.append({"name": i.name, "value": value})
            else:
                if new_value != old_value:
                    value = "[{}] ==> [{}]".format(old_value, new_value)
                    operate_detail.append({"name": i.name, "value": value})
        if operate_detail:
            print(operate_detail)
            models.OperationLog.objects.create(
                operator=operate_user,
                operate_type=models.OperationLog.MODIFY,
                operate_detail=operate_detail,
                operate_obj=new_obj._meta.object_name,
                operate_summary="修改" + new_obj._meta.verbose_name + str(new_obj),
            )

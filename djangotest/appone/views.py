from django.shortcuts import render

# Create your views here.
import copy
from django.views import View
from django.http import HttpResponse
from appone.models import Wife


class TestView(View):
    def get(self, request):
        # 1. create
        # Wife.objects.create(is_log=True, name='张珊', high=1, age=2, weight=2)

        # 2. save()
        # obj = Wife.objects.filter(id=53).first()
        # obj.name = 'eee'
        # obj.save(is_log=True)

        # 3. update
        # Wife.objects.filter(id=53).update(is_log=True, name='单独')

        # 4. delete
        # Wife.objects.filter(id=51).delete(is_log=True)

        # 5. delete
        # obj = Wife.objects.filter(id=52).first()
        # obj.delete(is_log=True)

        # 6. 批量更新
        a_dict = {53: {"name": 'aa', "high": 1, "age": 2, "weight": 3},
                  54: {"name": 'dd', "high": 1, "age": 2, "weight": 3},
                  55: {"name": 'ff', "high": 1, "age": 2, "weight": 3}}
        ids = [53, 54, 55]
        wifes = Wife.objects.filter(id__in=ids)
        update_objs = []
        for wife in wifes:
            wife.name = a_dict[wife.id]['name']
            update_objs.append(wife)
        Wife.objects.bulk_update(update_objs, ['name'], is_log=True)

        # 7. 批量创建
        # a_dict = {1: {"name": '我', "high": 1, "age": 2, "weight": 3},
        #           2: {"name": 'd点', "high": 1, "age": 2, "weight": 3},
        #           3: {"name": '44f锋', "high": 1, "age": 2, "weight": 3}}
        # ids = [1, 2, 3]
        # wifes = []
        # for i in ids:
        #     wifes.append(Wife(**a_dict[i]))
        # Wife.objects.bulk_create(wifes, is_log=True)

        print(1)
        return HttpResponse('11')

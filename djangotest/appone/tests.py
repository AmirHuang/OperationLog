# from datetime import datetime, timedelta
# from dateutil.parser import parse
#
#
# def filter_func(x):
#     if x:
#         now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         other_time = parse(now_time) + timedelta(15)
#         return parse(x) > parse(now_time) and parse(x) < other_time
#     else:
#         return False
#
#
# x = '2021-07-15 16:00'
# c = filter_func(x)
# print(c)

# t = "%Y-%m-%d %H:%M:%S"
# a = '2021-06-27 16:00'

# # a = datetime.strptime(a, t)
# # print(a)
# a = parse(a)
# print(a)
# print(type(a))
#
# now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# print(parse(now))
# print(parse(now) > a)
#
# c = parse(now) + timedelta(15)
# print(c)
# print(parse(''))


# d_order = sorted(d.items(), key=lambda x: x[1], reverse=False)

# items = {"vm": {1: 12, 5: 23, 6: 13}, "disk": {1: 112, 5: 22, 6: 33}, "eip": {1: 102, 5: 213, 6: 3}}
#
# for item in items:
#     items[item] = dict(sorted(items[item].items(), key=lambda x: x[1], reverse=True)[:2])
#
# print(items)

# items.pop()
import datetime

ss = {}

for i in range(30):
    xx = (datetime.datetime.now() - datetime.timedelta(i)).strftime('%Y-%m-%d')
    ss[xx] = 0
print(ss)

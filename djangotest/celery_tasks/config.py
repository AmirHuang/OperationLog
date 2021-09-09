import datetime
from celery.schedules import crontab
from kombu import Exchange, Queue

BROKER_URL = 'redis://localhost:6379/10'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/11'

CELERY_TIMEZONE = 'Asia/Shanghai'
# celery 设置
CELERY_ENABLE_UTC = False
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ["pickle", "json"]

# 队列

CELERY_QUEUES = (

    Queue("default", Exchange("default"), routing_key="default"),

    Queue("appone_add_queue", Exchange("appone_add_queue"), routing_key="appone_add_router"),

    Queue("apptwo_mult_queue", Exchange("apptwo_mult_queue"), routing_key="apptwo_mult_router")

)

# 路由

CELERY_ROUTES = {
    # 'appone_add': {"queue": "appone_add_queue", "routing_key": "appone_add_router"},
    #
    # 'apptwo_mult': {"queue": "apptwo_mult_queue", "routing_key": "apptwo_mult_router"}

}

# 定时任务配置如下

CELERYBEAT_SCHEDULE = {
    # 'beat_task1': {
    #     'task': 'appthree_comment',
    #
    #     'schedule': datetime.timedelta(seconds=2),
    #
    #     'args': (2, 8)
    #
    # },
    #
    # 'beat_task2': {
    #     'task': 'appthree_comment',
    #
    #     'schedule': crontab(hour=16, minute=32),
    #
    #     'args': (4, 5)
    #
    # }

}

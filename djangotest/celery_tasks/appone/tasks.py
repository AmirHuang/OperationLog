from celery_tasks.main import app

from appone.call_back import OperationLogFunc


@app.task(name='xxxx')
def operate_log_task(func_name, **kwargs):
    f = OperationLogFunc()
    getattr(f, func_name)(**kwargs)

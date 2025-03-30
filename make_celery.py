from celery import Celery
from main import create_app

def make_celery():
    celery = Celery(
        'tasks',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )
    # Set broker connection retry setting
    celery.conf.update({
        'broker_connection_retry_on_startup': True,
        'broker_connection_retry': True
    })
    flask_app,_ = create_app()

    celery.conf.update(flask_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery



celery_app = make_celery()

if __name__ == '__main__':
    celery_app.start()

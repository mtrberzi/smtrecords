from __future__ import absolute_import

from celery import Celery

app = Celery('smtrecords', include=['smtrecords.worker_tasks'])
app.config_from_object('smtrecords.celeryconfig')

if __name__ == '__main__':
        app.start()

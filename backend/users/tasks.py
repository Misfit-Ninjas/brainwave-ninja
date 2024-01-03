from django.core import management

from brainwave import celery_app


@celery_app.task
def clearsessions():
    management.call_command("clearsessions")

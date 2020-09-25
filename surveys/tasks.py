from how_distant.celery import app as celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task()
def send_sms_async(sms_id, **kwargs):
    logger.info("sending sms asynchronously")
    from surveys.models import SMS
    sms = SMS.objects.get(id=sms_id)

    sms.send()
    logger.info("sms sent")
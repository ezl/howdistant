from model_utils.models import TimeStampedModel
import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField 
from django.conf import settings

from twilio.rest import Client

if settings.TWILIO_ACCOUNT_SID:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def generate_short_uuid():
    return str(uuid.uuid4())[:8]

class BaseModel(TimeStampedModel):
    id = models.CharField(primary_key=True, default=generate_short_uuid, editable=False, max_length=256)
    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-created']
    
    def remove(self):
        self.is_removed = True
        self.save()

class SurveyForm(BaseModel):
    form = JSONField(null=True, blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return "{0} - {1}".format(self.id, self.default)

    def submit(self, answers, name=None, bundle=None):
        if not bundle:
            bundle = self.survey_bundles.create()

        new_survey = Survey.objects.create(answers=answers, name=name, bundle=bundle)
        new_survey.save()

        for survey in bundle.surveys.exclude(id=new_survey.id):
            if survey.phone_number:
                survey.send_sms_notification()

        return bundle, new_survey

class SurveyBundle(BaseModel):
    form = models.ForeignKey(SurveyForm, db_index=True, on_delete=models.CASCADE, related_name="survey_bundles")

    def __str__(self):
        return "{0} - {1}".format(self.id, self.form.id)

    @property
    def summary(self):
        summary = self.form.form.copy()

        for survey in self.surveys.all():
            for idx, question in enumerate(summary):
                answer = survey.answers[idx]
                if question.get('type') == 'radio':
                    answered_option = list(filter(lambda option: option.get('value') == answer, question.get('options')))
                    answered_option = [answered_option[0]['value']] + answered_option[0]['depend']
                else:
                    answered_option = answer

                for opt in question.get('options'):
                    if opt['value'] in answered_option:
                        if not opt.get('comfortable'):
                            opt['comfortable'] = []
                        opt['comfortable'].append(survey.name)
                    else:
                        if not opt.get('uncomfortable'):
                            opt['uncomfortable'] = []
                        opt['uncomfortable'].append(survey.name)
        return summary

class Survey(BaseModel):
    bundle = models.ForeignKey(SurveyBundle, db_index=True, on_delete=models.CASCADE, related_name="surveys")
    answers = JSONField(null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=256)
    phone_number = models.CharField(null=True, blank=True, max_length=20)

    def __str__(self):
        return "{0} - {1} by {2}".format(self.id, self.bundle, self.name)
    
    def send_sms_notification(self, new_survey=None):
        if not new_survey:
            new_survey = self.bundle.surveys.order_by('-modified').first()

        sms = SMS.objects.create(
            survey=self,
            to_phone=self.phone_number,
            body="[How Distant] {0} also responded. Check the group results here: https://howdistant.com/survey/{1}/summary \n Reply STOP to stop receiving notifications.".format(
                new_survey.name,
                self.bundle.id
            )
        )

        from surveys.tasks import send_sms_async
        send_sms_async.delay(sms.id)
        

class SMS(BaseModel):
    STATUS_NEW = "new"
    STATUS_SENT = "sent"
    STATUS_ERROR = "error"

    STATUS_CHOICES = (
        (STATUS_NEW, "new"),
        (STATUS_SENT, "sent"),
        (STATUS_ERROR, "error"),
    )

    TWILIO = "twilio"

    BACKEND_CHOICES = (
        (TWILIO, "twilio"),
    )
    
    survey = models.ForeignKey(Survey, db_index=True, on_delete=models.CASCADE, related_name="sms")
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_NEW, db_index=True, max_length=10)
    from_phone = models.CharField(max_length=32, default=settings.SMS_FROM_PHONE)
    to_phone = models.CharField(max_length=32, blank=True, null=True)
    external_id = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    backend_type = models.CharField(choices=BACKEND_CHOICES, default=TWILIO, max_length=10)

    @property
    def backend(self):
        return client
    
    def send(self):
        try:
            message = self.backend.messages.create(
                body=self.body,
                from_="+1{}".format(self.from_phone),
                to="+1{}".format(self.to_phone)
            )
            self.external_id = message.sid
            self.status = self.STATUS_SENT
            self.save()
        except Exception as e:
            self.status = self.STATUS_ERROR
            self.save()
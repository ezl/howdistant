from model_utils.models import TimeStampedModel
import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField 

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
        
        return bundle

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

class Survey(TimeStampedModel):
    bundle = models.ForeignKey(SurveyBundle, db_index=True, on_delete=models.CASCADE, related_name="surveys")
    answers = JSONField(null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=256)

    def __str__(self):
        return "{0} - {1} by {2}".format(self.id, self.bundle, self.name)

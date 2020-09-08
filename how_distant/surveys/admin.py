from django.contrib import admin

# Register your models here.
from .models import SurveyForm, SurveyBundle, Survey

admin.site.register(SurveyForm)
admin.site.register(SurveyBundle)
admin.site.register(Survey)
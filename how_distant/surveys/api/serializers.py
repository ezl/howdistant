from django.conf import settings
from rest_framework import serializers

from how_distant.surveys.models import SurveyForm, SurveyBundle, Survey

class SurveyFormSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = SurveyForm
        fields = '__all__'

class SurveySeralizer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Survey
        fields = ['id', 'name', 'answers', 'created', 'modified']

class SurveyBundleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(read_only=True)
    surveys = SurveySeralizer(many=True)
    form = SurveyFormSerializer()
    summary = serializers.SerializerMethodField()

    class Meta:
        model = SurveyBundle
        fields = ['id', 'surveys', 'form', 'summary']
    
    def get_summary(self, obj):
        return obj.summary



    
from rest_framework import routers, serializers, viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from how_distant.surveys.models import SurveyForm, SurveyBundle, Survey

from .serializers import SurveyFormSerializer, SurveyBundleSerializer, SurveySerializer
class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (AllowAny,)

    @action(detail=True, methods=['put'], permission_classes=[AllowAny])
    def enable_sms_notification(self, request, pk=None):
        survey = self.get_object()
        survey.phone_number = request.data.get('phone')
        survey.save()
        return Response({ "message": "SMS notification enabled."})

class SurveyBundleViewSet(viewsets.ModelViewSet):
    queryset = SurveyBundle.objects.all()
    serializer_class = SurveyBundleSerializer
    permission_classes = (AllowAny,)

class SurveyFormViewSet(viewsets.ModelViewSet):
    queryset = SurveyForm.objects.none()
    serializer_class = SurveyFormSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return SurveyForm.objects.filter(default=True)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def default(self, request):
        survey_form = SurveyForm.objects.filter(default=True).first()
        serialized = SurveyFormSerializer(survey_form, context={ "request": request })
        return Response(serialized.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def submit(self, request):
        survey_form = SurveyForm.objects.filter(default=True).first()
        answers = request.data.get('answers')
        name = request.data.get('name')
        bundle_id = request.data.get('bundle')

        if bundle_id:
            bundle = SurveyBundle.objects.get(id=bundle_id)
        else:
            bundle = None

        bundle, new_survey = survey_form.submit(answers, name=name, bundle=bundle)
        
        serialized = SurveyBundleSerializer(bundle, context={ "request": request })
        data = serialized.data.copy()
        data.update({
            "submitted_survey": SurveySerializer(new_survey, context={ "request", request }).data
        })
        return Response(data)
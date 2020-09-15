from rest_framework import routers, serializers, viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from how_distant.surveys.models import SurveyForm, SurveyBundle

from .serializers import SurveyFormSerializer, SurveyBundleSerializer

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

        bundle = survey_form.submit(answers, name=name, bundle=bundle)
        
        serialized = SurveyBundleSerializer(bundle, context={ "request": request })
        return Response(serialized.data)
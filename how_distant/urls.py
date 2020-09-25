from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework import routers
from surveys.api.viewsets import SurveyFormViewSet, SurveyBundleViewSet, SurveyViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'survey_forms', SurveyFormViewSet)
router.register(r'survey_bundles', SurveyBundleViewSet)
router.register(r'surveys', SurveyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/v1/', include(router.urls)),
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

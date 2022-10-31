from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils

router = routers.DefaultRouter()
router.register(r'api/document', views.DocumentViewSet, basename='document')
router.register(r'api/fragment', views.FragmentViewSet, basename='fragment')

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('context', 'api', exclude=['document']),
]
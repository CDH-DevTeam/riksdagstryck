from django.urls import path, include
from rest_framework import routers
from . import views
import diana.utils as utils

router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("riksdagstryck")
documentation = utils.build_app_api_documentation("riksdagstryck", endpoint)


router.register(rf'{endpoint}/document', views.DocumentViewSet, basename='document')
router.register(rf'{endpoint}/frequency', views.SearchCountViewSet, basename='frequency')

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('riksdagstryck', endpoint, exclude=['document',]),
    *documentation
]
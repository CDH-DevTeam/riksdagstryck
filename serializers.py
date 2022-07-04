from distutils import dep_util
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from diana.utils import DEFAULT_EXCLUDE
from . import models

from diana.abstract.models import get_fields

class DocumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = get_fields(models.Document, exclude=DEFAULT_EXCLUDE + ['text_vector'])

class FragmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    headline = serializers.CharField()

    class Meta:
        model = models.Document
        fields = get_fields(models.Document, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['headline']
        depth = 1

from distutils import dep_util
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin

from diana.utils import DEFAULT_EXCLUDE
from . import models

from diana.abstract.models import get_fields

class DocumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    excerpts = serializers.CharField(default="")

    class Meta:
        model = models.Document
        fields = get_fields(models.Document, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['excerpts']


class SearchCountSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    results = serializers.IntegerField(default=0)
    # splits = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = models.Document
        fields = ['year', 'results',]
        # fields = get_fields(models.RiksdagstryckDocument, exclude=DEFAULT_EXCLUDE + ['text_vector']) + ['excerpts']
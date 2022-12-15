import rest_framework
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers
from django_filters import rest_framework as filters

from diana.abstract.views import DynamicDepthViewSet
from diana.abstract.models import get_fields, DEFAULT_FIELDS
from rest_framework.compat import coreapi, coreschema
from django.utils.encoding import force_str
from django.contrib.postgres.aggregates import ArrayAgg, StringAgg

from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline
from django.db.models import IntegerField, TextField, F, Value, Count
from django.db.models.expressions import Func
from django.contrib.postgres.fields import ArrayField

class FragmentFilter(rest_framework.filters.BaseFilterBackend):

    search_param = 'search'
    search_title = 'Full-text search in the documents' # Shows up in DRF docs interactive query pop-up menu as the title for the query section of the field1
    search_description = 'Lists excerpts, or fragments, containing the search term.'

    def filter_queryset(self, request, queryset, view):


        config = 'simple'
        fragment_delimiter = '...<br/><br/>...'

        text          = request.query_params.get('search', None)

        max_fragments = request.query_params.get('max_fragments', 1000)
        max_words = request.query_params.get('max_words', 50)
        min_words = request.query_params.get('min_words', 10)

        if text:
            search_vector   = SearchVector("text_vector")
            search_query    = SearchQuery(text),
            search_rank     = SearchRank(search_vector, search_query)

            queryset = (
                queryset
                    .filter(text_vector=SearchQuery(text, search_type='raw', config=config))
                    .annotate(
                        excerpts = SearchHeadline(
                                    'text',
                                    SearchQuery(text, search_type='raw', config=config),
                                    config=config, 
                                    max_fragments=max_fragments, 
                                    max_words=max_words, 
                                    min_words=min_words, 
                                    fragment_delimiter=fragment_delimiter
                                )
                        # rank=search_rank
                        )

                    .order_by("id")
            )

        return queryset

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
                coreapi.Field(
                    name=self.search_param,
                    required=False,
                    location='query',
                    schema=coreschema.String(
                        title=force_str(self.search_title),
                        description=force_str(self.search_description)
                    )
                )
            ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.search_description),
                'schema': {
                    'type': 'string',
                },
            },
        ]


class DocumentFilter(filters.FilterSet):

    min_year = filters.NumberFilter(field_name="year", lookup_expr='gte')
    max_year = filters.NumberFilter(field_name="year", lookup_expr='lte')
    # cat = filters.CharFilter(field_name="category__abbreviation", lookup_expr='in')
    cat = filters.CharFilter(field_name="category__abbreviation", lookup_expr='iexact')

    class Meta:
        model = models.Document
        fields = [field for field in get_fields(models.Document, exclude=DEFAULT_FIELDS + ['text_vector'])]
        


class DocumentViewSet(DynamicDepthViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    filter_backends = [DjangoFilterBackend, FragmentFilter, OrderingFilter]
    filterset_class = DocumentFilter
    ordering_fields = ['year', 'category']
    ordering = ['year']

class SearchCountViewSet(DynamicDepthViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.SearchCountSerializer
    filter_backends = [DjangoFilterBackend, FragmentFilter]
    filterset_class = DocumentFilter

    def filter_queryset(self, queryset):

        split_strings = Func(
            F('strings'),
            Value('...<br/><br/>...'),
            function='regexp_split_to_array',
            output_field=ArrayField(TextField())
        )

        count_strings = Func(
            F('splits'),
            Value(1),
            function='array_length',
            output_field=IntegerField()
        )

        # super needs to be called to filter backends to be applied
        queryset = super().filter_queryset(queryset)
        # some extra filtering

        queryset = queryset.values('year')\
            .annotate(strings=StringAgg('excerpts', delimiter="...<br/><br/>...", output_field=TextField()))\
            .annotate(splits=split_strings)\
            .annotate(results=count_strings)\
            .order_by('year')\
            .values('year','results')

        return queryset
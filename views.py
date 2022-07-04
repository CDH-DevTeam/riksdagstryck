from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers
from django.db.models import F

from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector, SearchRank

from diana.abstract.views import CountModelMixin, GenericPagination

class DocumentViewSet(viewsets.ModelViewSet, CountModelMixin):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    pagination_class = GenericPagination
    filter_backends = [DjangoFilterBackend]

class FragmentViewSet(viewsets.ModelViewSet):
    
    serializer_class = serializers.FragmentSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = GenericPagination

    def get_queryset(self):

        # Defines a "simple" configuration which only tokenizes words, and does not stem or lemmatize
        config = 'simple'
        fragment_delimiter = '...<br/><br/>...'


        queryset = models.Document.objects.all()

        text          = self.request.query_params.get('text', None)
        max_fragments = self.request.query_params.get('max_fragments', 1000)
        max_words = self.request.query_params.get('max_words', 50)
        min_words = self.request.query_params.get('min_words', 20)

        if text:
            search_vector   = SearchVector("text_vector")
            search_query    = SearchQuery(text, config=config, search_type='raw'),
            search_rank     = SearchRank(search_vector, search_query)

            search_headline = SearchHeadline(
                                    F('text'),
                                    search_query,
                                    config=config, 
                                    max_fragments=max_fragments, 
                                    max_words=max_words, 
                                    min_words=min_words, 
                                    fragment_delimiter=f'{fragment_delimiter}'
                                )

            queryset = (
                queryset
                    .filter(text_vector=text)
                    .annotate(headline = search_headline, rank=search_rank)
                    .order_by("-rank")
                    .values('name', 'year', 'chamber', 'category', 'headline' )
            )


        return queryset
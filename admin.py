from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from diana.utils import get_fields, DEFAULT_EXCLUDE, DEFAULT_FIELDS

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    fields = get_fields(Document, exclude=DEFAULT_EXCLUDE+['text_vector'])
    readonly_fields = ['uuid', *DEFAULT_FIELDS]
    list_display = ['name', 'category', 'year']
    list_filter = ['name', 'category', 'year']
    search_fields = ['name', 'category']
    list_filter = ['category']


from django.db import models
import diana.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.indexes import GinIndex # add the Postgres recommended GIN index 
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

        
class DocumentCategory(abstract.AbstractBaseModel):

    name = abstract.CINameField(max_length=128, verbose_name=_("name"), help_text=_("The name of the document as provided by the Swedish Royal Library."))
    abbreviation = abstract.CINameField(max_length=32, verbose_name=_("abbreviation"))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:

        return str(self)

class Document(abstract.AbstractDocumentModel):

    name        = models.CharField(max_length=128, unique=True, verbose_name=_("name"))
    year        = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("year"))
    category    = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, null=True, verbose_name=_("category"))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:

        return str(self)


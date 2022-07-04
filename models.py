from django.db import models
import diana.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.indexes import GinIndex # add the Postgres recommended GIN index 

class TermFrequency(abstract.AbstractBaseModel):

    year = models.PositiveIntegerField(verbose_name=_("year"))
    word = models.CharField(max_length=512, verbose_name=_("word"))
    ndoc = models.PositiveIntegerField(verbose_name=_("riksdagstryck.termfrequency.ndoc"))
    nentry = models.PositiveIntegerField(verbose_name=_("riksdagstryck.termfrequency.nentry"))   

    def __str__(self):

        return f"{self.word}: {self.nentry} entries in {self.ndoc} docs ({self.year})"
        
class Category(abstract.AbstractBaseModel):

    name = abstract.CINameField(max_length=128, primary_key=True, verbose_name=_("name"))
    abbreviation = abstract.CINameField(max_length=32, verbose_name=_("abbreviation"))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:

        return str(self)

class Document(abstract.AbstractDocumentModel):
    
    CHAMBER_CHOICES = (
        ('fk', 'första kammaren'),
        ('ak', 'andra kammaren'),
    )

    name        = models.CharField(max_length=128, unique=True, verbose_name=_("name"))
    year        = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("year"))
    chamber     = models.CharField(max_length=2, choices=CHAMBER_CHOICES, blank=True, null=True, verbose_name=_("riksdagstryck.document.chamber"))

    category    = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name=_("category"))

    nwords     = models.PositiveIntegerField(default=0, verbose_name=_("riksdagstryck.document.nwords"))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:

        return str(self)

    class Meta:
        indexes = (GinIndex(fields=["text_vector"]),)



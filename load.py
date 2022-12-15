#%%
from .models import *
from django.db import transaction

#%%
import os
import json
from glob import glob
import re 
from tqdm import tqdm

def metadata_from_riksdagstryck(path):

    splits = path.split("/")

    name = splits[-1].replace('.txt', '')

    year = int(name[0:4])

    return {'name': name, 'year': year}

def text_from_riksdagstryck(path):

    with open(path, "r") as f:
        text = f.read()

    return text

def documents_to_db(root, extension="jpg"):

    files = glob(os.path.join(root, f"*.{extension}"))
    documents = []

    for file in tqdm(files):

        # Extract metadata from the filename
        metadata = metadata_from_riksdagstryck(file)

        if metadata:
            
            # Read the text
            text     = text_from_riksdagstryck(file)

        else:
            continue

        # Create or fetch the document with matching metadata and text
        # documents.append(riksdagstryck.models.Document(**metadata, text=text))
        Document.objects.get_or_create(**metadata, text=text)

    # Create all documents at once
    # riksdagstryck.models.Document.objects.bulk_create(documents)


@transaction.atomic
def documents_to_postgres():
    Document.objects.all().delete()

    categories = {
        'tvåkammarriksdagen-1867-1970-berättelser-redogörelser-frsrdg':     {'name': 'Berättelser, redogörelser', 'abbreviation': 'frsrdg'},
        'tvåkammarriksdagen-1867-1970-betänkanden-memorial-utlåtanden':     {'name': 'Betänkanden, memorial, utlåtanden', 'abbreviation': 'bet'},
        'tvåkammarriksdagen-1867-1970-motioner':                            {'name': 'Motioner', 'abbreviation': 'mot'},
        'tvåkammarriksdagen-1867-1970-propositioner-skrivelser':            {'name': 'Propositioner, skrivelser', 'abbreviation': 'prop'},
        'tvåkammarriksdagen-1867-1970-protokoll':                           {'name': 'Protokoll, beslut', 'abbreviation': 'prot'},
        'tvåkammarriksdagen-1867-1970-register':                            {'name': 'Register', 'abbreviation': 'reg'},
        'tvåkammarriksdagen-1867-1970-reglementen-sfs':                     {'name': 'Reglementen', 'abbreviation': 'sfs'},
        'tvåkammarriksdagen-1867-1970-riksdagens-författningssamling-rfs':  {'name': 'Riksdagens författningssamling', 'abbreviation': 'rfs'},
        'tvåkammarriksdagen-1867-1970-riksdagsskrivelser-rskr':             {'name': 'Riksdagsskrivelser', 'abbreviation': 'rskr'},
        'tvåkammarriksdagen-1867-1970-utredningar-kombet-sou':              {'name': 'Statens offentliga utredningar', 'abbreviation': 'sou'},
    }

    root = "/media/vws/Demeter2/xwahvi/riksdagstryck/"

    for category, properties in tqdm(categories.items()):

        path    = os.path.join(root, category, '*.txt')
        files   = glob(path)

        # Get a category object
        c, _ = DocumentCategory.objects.get_or_create(**properties)
        docs = []
        for file in tqdm(files, leave=False):
            
            # Extract the relevant data from the paths
            metadata = metadata_from_riksdagstryck(file)
            text     = text_from_riksdagstryck(file)

            # Get or create the document
            doc = Document(year=metadata['year'], name=metadata['name'], category=c, text=text)

            docs.append(doc)

            if len(docs) > 500:
                Document.objects.bulk_create(docs)
                docs = []

        if len(docs) > 0:
            Document.objects.bulk_create(docs)
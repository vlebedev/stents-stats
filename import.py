#!/usr/bin/env python

import subprocess
import datetime

from pymongo import MongoClient


def unix_to_str_date(u):
    return datetime.datetime.fromtimestamp(u).strftime('%d.%m.%Y')


client = MongoClient('mongodb://localhost:27017/')
db = client.stents
cards = db.cards
csvexp = db.csvexp

# clear the export collection
csvexp.remove()

# unwind cards collection around stents array
pipeline = [{'$unwind': '$stents'}]
unwound_cards = cards.aggregate(pipeline)

# save unwound documents into csvexp collection
# patch _id and createdAt
for doc in unwound_cards[u'result']:
    doc[u'patient_id'] = doc[u'_id']
    doc[u'createdAt'] = unix_to_str_date(int(doc[u'createdAt'] / 1000))
    del doc[u'_id']
    csvexp.insert(doc)

# generate csv file using mongoexport utility
out = subprocess.getoutput(
    'mongoexport -d stents -c csvexp -o ./in/stents.csv '
    '-fieldFile ./in/fields.txt --csv')
print(out)

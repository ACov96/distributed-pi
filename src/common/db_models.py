import os
from mongoengine import connect, Document, DateTimeField, LongField, StringField

## Setup database connection
assert 'DB_URI' in os.environ, "Missing DB_URI environment variable"
DB_URI = os.environ['DB_URI']
connect(host=DB_URI)
print("Connected to MongoDB instance: {}".format(DB_URI))

## Database models
class Jobs(Document):
    """
    Describes a set of digit indices for a client to generate. 

    The range can be defined as:
        [digit_index_start, digit_index_end)

    In other words, the job set describes the computation from 
    digit_index_start up to BUT NOT INCLUDING digit_index_end.
    """
    expirey = DateTimeField(required=True)
    digit_index_start = LongField(required=True)
    digit_index_end = LongField(required=True)

class Base16Results(Document):
    """
    Single base-16 value at a given index of Pi.
    """
    submit_time = DateTimeField(required=True)
    digit_index = LongField(required=True)
    digit_value = StringField(required=True)

class DBLock(Document):
    """
    Database-level lock to synchronize across servers
    """
    expirey = DateTimeField(required=True)
    meta = {'max_documents':1}
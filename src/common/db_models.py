import os
import time
from datetime import datetime, timedelta
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

def db_lock_enter():
    while True:
        try:
            l = DBLock(expirey=(datetime.now() + timedelta(seconds=15)))
            l.save()
            break
        except:
            if DBLock.objects().filter(expirey__lt=datetime.now()).count() != 0:
                DBLock.drop_collection()
            else:
                time.sleep(.1)

def db_lock_leave():
    DBLock.drop_collection()

class PrioritizedJobs(Document):
    """
    One-off jobs that need to be run or re-run for some reason.
    These jobs will be prioritized above creating new jobs.
    """
    digit_index_start = LongField(required=True)
    digit_index_end = LongField(required=True)

class Base16Render(Document):
    """
    Concatenated string of Base16Results instances for a contiguous index region starting at index 1.
    """
    render = StringField(required=True)
    created = DateTimeField(required=True)

class Base10Render(Document):
    """
    Final Pi result in base 10.
    """
    render = StringField(required=True)
    created = DateTimeField(required=True)

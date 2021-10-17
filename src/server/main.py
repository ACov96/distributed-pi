import os
import json
import time
import threading
from bottle import get, post, run, request, response
from datetime import datetime, timedelta
from common.db_models import Jobs, Base16Results, DBLock

## Constants
JOB_TIMEOUT = 30 if 'JOB_TIMEOUT' not in os.environ else os.environ['JOB_TIMEOUT']

## Helper functions
def db_lock_enter():
    while True:
        try:
            l = DBLock(expirey=(datetime.now() + timedelta(seconds=15)))
            break
        except:
            if DBLock.objects().filter(expirey__lt=datetime.now()).count() != 0:
                DBLock.drop_collection()
            else:
                time.sleep(.1)

def db_lock_leave():
    DBLock.drop_collection()

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def cleanup_expired_jobs():
    db_lock_enter()
    Jobs.objects().filter(expirey__lte=datetime.now()).delete()
    db_lock_leave()


## Helper threads
# job_cleanup_thread = set_interval(cleanup_expired_jobs, JOB_TIMEOUT)


## Routes
@get('/job-timeout')
def report_job_timeout():
    response.headers['Content-Type'] = 'application/json'
    return [json.dumps({"timeout": JOB_TIMEOUT})]

@post('/request-jobs')
def request_job():
    db_lock_enter()
    response.headers['Content-Type'] = 'application/json'

    # Compute job expiration time
    now = datetime.now()
    expirey = now + timedelta(seconds=JOB_TIMEOUT)

    # Compute digit index for job to compute
    # TODO: max_result_digit_index is incorrect because it could potentially skip over any non-contiguous gaps.
    #       Need to pull from a PriorityQueue document, but that is not currently implemented.
    num_requested = request.json.get('num_jobs')
    active_jobs = Jobs.objects().filter(expirey__gt=now).order_by('-digit_index_end')
    base16_results = Base16Results.objects().order_by('-digit_index')

    if active_jobs.count() == 0:
        max_active_job_digit_index = 1 
    else:
        max_active_job_digit_index = active_jobs.first().digit_index_end

    if base16_results.count() == 0:
        max_result_digit_index = 0 
    else: 
        max_result_digit_index = base16_results.first().digit_index

    next_digit_index_start = max(max_active_job_digit_index, max_result_digit_index + 1)
    next_digit_index_end = next_digit_index_start + num_requested

    # Create the job and send it to the client
    new_job = Jobs(expirey=expirey, digit_index_start=next_digit_index_start, digit_index_end=next_digit_index_end)
    new_job.save()
    db_lock_leave()
    return [new_job.to_json()]

@post('/submit-job')
def submit_job():
    db_lock_enter()
    response.headers['Content-Type'] = 'application/json'
    now = datetime.now()
    job = Jobs.objects.get(id=request.json.get('job_id'))

    if job.expirey < now:
        print("Job {} has expired".format(job.id))
        response.status = 500
        return [json.dumps({"error":"Job {} has expired.".format(job.id)})]

    digits = request.json.get('digits')
    if len(digits) != (job.digit_index_end - job.digit_index_start):
        print("Bad digits for job {}".format(job.id))
        print("len(digits) = {}".format(len(digits)))
        print(digits)
        response.status = 500
        return [json.dumps({"error": "Number of submitted digits does not match job"})]

    digit_index = job.digit_index_start
    for v in digits:
        result = Base16Results(submit_time=now, digit_index=digit_index, digit_value=v)
        result.save()
        digit_index += 1
    job.delete()
    db_lock_leave()
    return [json.dumps({"message": "Job submitted successfully."})]


## Run the server
print("Using job timeout: {} seconds".format(JOB_TIMEOUT))
run(host='0.0.0.0', port=8080, debug=True)
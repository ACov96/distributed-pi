import requests
import multiprocessing
import time
import os
from datetime import datetime, timedelta
from pprint import pprint
from common.pi_compute import compute_base16_pi_digit

assert os.environ.get('BASE_SERVER_URI'), "Missing server URI environment variable"
BASE_URI = os.environ.get('BASE_SERVER_URI')
REQUEST_JOB_URL = '{}/request-jobs'.format(BASE_URI)
SUBMIT_JOB_URL = '{}/submit-job'.format(BASE_URI)
JOB_TIMEOUT_URL = '{}/job-timeout'.format(BASE_URI)

ITEMS_PER_JOB = 100

def request_job():
    r = requests.post(REQUEST_JOB_URL, json={"num_jobs": ITEMS_PER_JOB})
    r_json = r.json()
    assert r.status_code == 200, "Failed to request job"
    return {"job_id": r_json.get("_id").get("$oid"), 
            "start_index": r_json.get('digit_index_start'),
            "stop_index": r_json.get('digit_index_end')}

def do_job(job):
    start_index = job.get("start_index")
    stop_index = job.get("stop_index")
    print("Working on job {} from [{},{})".format(job.get("job_id"), start_index, stop_index))
    digits = []
    for n in range(start_index, stop_index):
        digits.append(compute_base16_pi_digit(n))
    return digits

def submit_job(job, digits):
    global ITEMS_PER_JOB
    print("Submitting job: {}".format(job.get("job_id")))
    r = requests.post(SUBMIT_JOB_URL, json={"job_id":job.get("job_id"),"digits":digits})
    if r.status_code == 200:
        print("Submitted job {} successfully".format(job.get("job_id")))
    else:
        print("Failed to submit job {}".format(job.get("job_id")))
        pprint(r.content)
        ITEMS_PER_JOB /= 2
        if ITEMS_PER_JOB <= 0:
            ITEMS_PER_JOB = 1

## Estimate throughput
r = requests.get(JOB_TIMEOUT_URL)
if r.status_code != 200:
    print("Couldn't get API job timeout, assuming {} items for each job request is optimal.".format(ITEMS_PER_JOB))
else:
    r_json = r.json()
    timeout = r_json.get("timeout")
    done_time = datetime.now() + timedelta(seconds=int(timeout * .8))
    print("Estimating throughput")

    start_time = datetime.now()
    item_count = 0
    start_index = 100000
    while datetime.now() < done_time:
        for n in range(start_index, start_index + 10):
            compute_base16_pi_digit(n)
        item_count += 10
        start_index += 10

    end_time = datetime.now()
    total_time = end_time - start_time
    item_count = max(item_count, 1)
    print("Optimal throughput is {} items/second ({} total items over {} seconds)".format(int(item_count/total_time.total_seconds()), item_count, total_time.total_seconds()))
    ITEMS_PER_JOB = item_count

## Main work loop
def worker_loop():
    while True:
        job = request_job()
        digits = do_job(job)
        submit_job(job, digits)

NUM_WORKERS = int(os.environ.get("NUM_WORKERS", multiprocessing.cpu_count()))
print("Spawning {} workers".format(NUM_WORKERS))
workers = []
for i in range(0, NUM_WORKERS-1):
    p = multiprocessing.Process(target=worker_loop)
    p.start()
    workers.append(p)

worker_loop()

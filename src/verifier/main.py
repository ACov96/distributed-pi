import os
import time
from datetime import datetime
from common.db_models import Base16Results, PrioritizedJobs, Jobs
from common.utils import set_interval

BASE16_VERIFIER_INTERVAL = 60 if 'BASE16_VERIFIER_INTERVAL' not in os.environ else os.environ['BASE16_VERIFIER_INTERVAL']

def base16_verifier():
    print("Starting verification")
    last_value = ''
    last_index = 0
    for result in Base16Results.objects().order_by('+digit_index'):
        if result.digit_index == (last_index + 1):
            last_index = result.digit_index
            last_value = result.digit_value
        elif result.digit_index == last_index:
            assert last_value == result.digit_value, "Mismatch in value -- Base16Results[index={}] = {} != Base16Results[index={}] = {}".format(last_index, last_value, result.digit_index, result.digit_value)
        elif PrioritizedJobs.objects.filter(digit_index_start=(last_index+1),digit_index_end=result.digit_index).count() == 0 \
            and Jobs.objects.filter(digit_index_start=(last_index+1),digit_index_end=result.digit_index,expirey__gt=datetime.now()).count() == 0:
            print("Non-contiguous region between Base16Results[index={}] and Base16Results[index{}], submitting new PrioritizedJobs".format(last_index, result.digit_index))
            pj = PrioritizedJobs(digit_index_start=(last_index+1), digit_index_end=result.digit_index)
            pj.save()
            print("Submitted PrioritizedJob {}".format(pj.id))
    print("Finished verification")

def main():
    print("Setting Base16Results verifier to {} second interval".format(BASE16_VERIFIER_INTERVAL))
    base16_verifier_thread = set_interval(base16_verifier, BASE16_VERIFIER_INTERVAL)

    while True:
        if not base16_verifier_thread.is_alive():
            print("Restarting Base16 verifier")
            base16_verifier_thread.cancel()
            base16_verifier_thread = set_interval(base16_verifier, BASE16_VERIFIER_INTERVAL)
        time.sleep(10)

if __name__ == "__main__":
    main()
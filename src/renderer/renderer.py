import time
import os
import decimal
from datetime import datetime, timedelta
from tqdm import tqdm

MIN_WAIT = timedelta(seconds=60 if 'MIN_WAIT' not in os.environ else os.environ['MIN_WAIT'])

# TODO: Eventually, Python's decimal module may no longer have the ability to compute
#       the precision needed since it is bound by decimal.MAX_PREC, but that might be a ways away.
# DECIMAL_CONTEXT = decimal.getcontext()
# DECIMAL_CONTEXT.prec = 20_000_000_000_000 # decimal.MAX_PREC

def wait_until_next_cycle(render_start):
    if datetime.now() < (render_start + MIN_WAIT):
        time.sleep(MIN_WAIT.total_seconds())

def base16_render_loop():
    from common.db_models import Base16Results, Base16Render
    while True:
        print("Starting new Base16 render...")
        render_start = datetime.now()
        current_render = '3.'
        last_index = 0
        results = Base16Results.objects.all().order_by('+digit_index')
        assert results.first().digit_index == 1, "Bad first index"
        for result in tqdm(results,desc="Base16 Render"):
            if result.digit_index == (last_index + 1):
                current_render += result.digit_value
            elif result.digit_index == last_index:
                assert current_render[-1] == result.digit_value, "Odd mismatch, potentially corrupt region at index {}".format(result.digit_index)
            else:
                break
            last_index += 1
        render = Base16Render(created=datetime.now(), render=current_render)
        render.save()
        print("Created Base16 render {}".format(render.id))

        wait_until_next_cycle(render_start)

def base10_render_loop():
    """
    Conversion explained in this thread:
        https://math.stackexchange.com/questions/745668/base-16-to-base-10-number-conversion
    """
    from common.db_models import Base16Render, Base10Render
    DECIMAL_16 = decimal.Decimal(16)
    while True:
        render_start = datetime.now()
        print("Starting Base16 -> Base10 conversion")
        latest_base16_render = Base16Render.objects.order_by('-created').first()
        
        decimal.getcontext().prec = 20_000_000_000_000 # len(latest_base16_render.render)

        decimal_render = decimal.Decimal('3.0')
        exp = -1
        to_render = latest_base16_render.render[2:]

        for n in tqdm(to_render,desc="Base10 Render"):
            base = decimal.Decimal(int(n, base=16))
            decimal_render += base * (DECIMAL_16 ** exp)
            exp -= 1

        string_render = str(decimal_render)
        base10_render = Base10Render(created=datetime.now(),render=string_render)
        base10_render.save()
        print("Finished Base16 -> Base10 conversion: {}".format(base10_render.id))
        print(str(base10_render.render))

        wait_until_next_cycle(render_start)

if __name__ == "__main__":
    base10_render_loop()
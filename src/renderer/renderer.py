import time
import os
from datetime import datetime, timedelta
MIN_WAIT = timedelta(seconds=60 if 'MIN_WAIT' not in os.environ else os.environ['MIN_WAIT'])

def base16_render_loop():
    from common.db_models import Base16Results, Base16Render
    while True:
        print("Starting new render...")
        render_start = datetime.now()
        current_render = '3.'
        last_index = 0
        results = Base16Results.objects.all().order_by('+digit_index')
        assert results.first().digit_index == 1, "Bad first index"
        for result in results:
            if result.digit_index == (last_index + 1):
                current_render += result.digit_value
            elif result.digit_index == last_index:
                assert current_render[-1] == result.digit_value, "Odd mismatch, potentially corrupt region at index {}".format(result.digit_index)
            else:
                break
            last_index += 1
        render = Base16Render(created=datetime.now(), render=current_render)
        render.save()
        print("Created render {}".format(render.id))

        if datetime.now() < (render_start + MIN_WAIT):
            time.sleep(MIN_WAIT.total_seconds())

if __name__ == "__main__":
    base16_render_loop()
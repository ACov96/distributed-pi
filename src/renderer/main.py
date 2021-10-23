import time
import multiprocessing
from renderer import base16_render_loop, base10_render_loop
from render_server import start_render_server

if __name__ == "__main__":
    base16_render_process = multiprocessing.Process(target=base16_render_loop)
    base16_render_process.start()

    base10_render_process = multiprocessing.Process(target=base10_render_loop)
    base10_render_process.start()

    render_server_process = multiprocessing.Process(target=start_render_server)
    render_server_process.start()

    while True:
        time.sleep(10)
        if not base10_render_process.is_alive():
            print("Restarting Base10 renderer")
            base10_render_process.terminate()
            base10_render_process = multiprocessing.Process(target=base10_render_loop)
            base10_render_process.start()

        if not base16_render_process.is_alive():
            print("Restarting Base16 renderer")
            base16_render_process.terminate()
            base16_render_process = multiprocessing.Process(target=base16_render_loop)
            base16_render_process.start()

        if not render_server_process.is_alive():
            print("Restarting render server")
            render_server_process.terminate()
            render_server_process = multiprocessing.Process(target=start_render_server)
            render_server_process.start()
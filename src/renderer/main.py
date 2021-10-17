import multiprocessing
from renderer import base16_render_loop
from render_server import start_render_server

if __name__ == "__main__":
    base16_render_process = multiprocessing.Process(target=base16_render_loop)
    base16_render_process.start()

    start_render_server()

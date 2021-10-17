import json
from bottle import get, run, response

@get('/latest/base16')
def latest_render():
    from common.db_models import Base16Render
    response.headers['Content-Type'] = 'application/json'
    render = Base16Render.objects.order_by('-created').first()
    if render:
        return [render.to_json()]
    else:
        return [json.dumps({"message": "No renders available. Try again later"})]

## Run the server
def start_render_server():
    run(host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
    start_render_server()
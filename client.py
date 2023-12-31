import argparse

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading
import uvicorn

from pisync.lib.api.info_response import InfoResponse
from pisync.lib.media import Media
from pisync.lib.video import Video

from pisync.socket_handlers.client import connect_to_server, send_server_media_dump_message

from setup_db import setup_client_db
import settings

app = FastAPI()
settings.APP_TYPE = 'client'
templates = Jinja2Templates(directory="templates")

# Threads
app.stop_flag = threading.Event()
app.active_threads = []


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("client-index.html", {"request": request})


@app.get('/info')
def get_server_info():
    return InfoResponse(is_client=True)


@app.post("/play/{file_path}")
def play_media(file_path: str):
    media = Media.get_by_file_path(file_path)

    if media.client_id:
        raise Exception('This is a client - cannot play remote media!')

    print(f"Playing local media ({media.name})...")
    media.play()
    return


@app.post('/media/upload')
async def upload_media(file: UploadFile = File(...)):
    file_obj = await file.read()
    filename = file.filename
    new_file = await Media.create(file_obj, filename)

    send_server_media_dump_message()

    return new_file


@app.on_event("shutdown")
async def shutdown_event():
    app.stop_flag.is_set()

    for thread in app.active_threads:
        print(f"CLOSING {thread}...")
        thread.join()

    print("READY FOR SHUTDOWN.")


def setup(no_video: bool = False):
    setup_client_db()

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    socket_thread = threading.Thread(target=connect_to_server, args=(app,))
    socket_thread.start()

    # Start VLC
    if not no_video:
        Video.open_vlc(fullscreen=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the PiSync Client")
    parser.add_argument('--no-video', action='store_true', help='If passed, does not show video. Useful for debugging/viewing logs.')
    args = parser.parse_args()

    setup(args.no_video)
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)

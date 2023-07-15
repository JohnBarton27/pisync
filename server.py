from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sqlite3
import threading
import uvicorn

from pisync.lib.api.media_update_request import MediaUpdateRequest
from pisync.lib.media import Media


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    stored_media = Media.get_all_from_db()
    return templates.TemplateResponse("index.html", {"request": request,  "existing_media": stored_media})


@app.post("/play/{media_id}")
def play_media(media_id: int):
    media = Media.get_by_id(media_id)
    print(f"Playing {media.name}...")
    media.play(start_time=10, end_time=13)
    return


@app.put("/media/update")
def update_media(media_update: MediaUpdateRequest):
    media = Media.get_by_id(media_update.db_id)
    media.update_name(media_update.name)

    media = Media.get_by_id(media_update.db_id)
    return media


@app.get("/play")
def play():
    from pisync.lib.audio import Audio
    full_audio_track = Audio(file_path='/home/john/git/pisync/media/HauntedMansion_Audio.mp3', name='HM Audio')
    t1 = threading.Thread(target=full_audio_track.play, kwargs={'start_time': 10, 'end_time': 13})
    t1.start()
    print('Finished playing!')


def setup():
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Setup DB
    database_file = "pisync.db"
    app.db_conn = sqlite3.connect(database_file)
    app.db_cursor = app.db_conn.cursor()

    # Define the Media table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        file_name TEXT UNIQUE,
        file_type TEXT
    )
    """
    app.db_cursor.execute(create_table_query)

    # Create the 'media' folder if it doesn't exist
    media_dir = os.path.join(os.getcwd(), 'media')
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Find all media files in the 'media' folder
    from pisync.lib.media import Media
    media_files = Media.get_all_files()

    # Check if each file exists in the database, and if not, add it
    for media in media_files:
        if not media.exists_in_database():
            media.insert_to_db()


if __name__ == "__main__":
    setup()
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request, WebSocket, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import socket
import threading
import uvicorn

from pisync.lib.api.client_connect_request import ClientConnectRequest
from pisync.lib.api.client_search_response import Client as ApiClient, ClientSearchResponse
from pisync.lib.api.cue_update_request import CueUpdateRequest
from pisync.lib.api.create_cue_request import CreateCueRequest
from pisync.lib.api.info_response import InfoResponse
from pisync.lib.api.media_update_request import MediaUpdateRequest
from pisync.lib.client import Client as ClientObj
from pisync.lib.cue import Cue
from pisync.lib.media import Media
from pisync.lib.message import MediaPlayRequestMessage, MediaStopRequestMessage, MediaDeleteRequestMessage

from pisync.socket_handlers.server import connect_to_clients

import settings
from setup_db import setup_server_db


app = FastAPI()
settings.APP_TYPE = 'server'
templates = Jinja2Templates(directory="templates")

# Threads
app.stop_flag = threading.Event()
app.active_threads = []

app.connected_clients = set()
app.client_sockets = []

app.playing_media = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app.connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages from the client if needed
            pass
    except:
        app.connected_clients.remove(websocket)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    stored_media = Media.get_all_from_db()
    stored_clients = ClientObj.get_all_from_db()
    stored_cues = Cue.get_all_from_db()
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "existing_media": stored_media,
                                                     "existing_clients": stored_clients,
                                                     "existing_cues": stored_cues})


@app.get('/info')
def get_server_info():
    return InfoResponse(is_server=True)


@app.post('/clients/search')
def search_for_clients():
    existing_clients = ClientObj.get_all_from_db()

    # Get the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # TODO this might only work with an internet connection
    local_ip = s.getsockname()[0]
    s.close()

    # Create a range of IP addresses in the local network
    ip_range = local_ip[:local_ip.rfind('.')] + '.0/24'

    found_clients = []

    # Search for IPs with Port 8000 open
    for i in range(135, 145):
        ip = ip_range[:ip_range.rfind('.')] + '.' + str(i)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, settings.API_PORT))
            if result == 0:
                # Check the response body for 'is_client' == True
                response = requests.get(f"http://{ip}:{settings.API_PORT}/info")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('is_client'):
                        try:
                            hostname = socket.gethostbyaddr(ip)[0]
                            found_client = ApiClient(hostname=hostname, ip_address=ip)

                            # Only look for "new" clients here
                            if not any([existing_client.hostname == found_client.hostname for existing_client in existing_clients]):
                                found_clients.append(found_client)

                        except socket.herror:
                            print("Failed to retrieve the hostname")
                else:
                    print(f"Failed to retrieve info from IP {ip}. Status code: {response.status_code}")
            sock.close()
        except socket.error:
            pass

    return ClientSearchResponse(clients=found_clients)


@app.post('/client/add')
def add_client(request: ClientConnectRequest):
    print(f'Request to add clients: {request.clients}')

    for client in request.clients:
        client_obj = ClientObj(hostname=client.hostname, friendly_name=client.hostname, ip_address=client.ip_address)
        client_obj.insert_to_db()

    all_clients = ClientObj.get_all_from_db()

    return all_clients


@app.post("/play/{media_id}")
def play_media(media_id: int):
    media = Media.get_by_id(media_id)

    if media.client_id:
        client_obj = ClientObj.get_by_id(media.client_id)
        print(f'Looking for client {client_obj.hostname}...')
        for cli_socket in app.client_sockets:
            if cli_socket.getpeername()[0] == client_obj.ip_address:
                message = MediaPlayRequestMessage(media.file_path)
                message.send(cli_socket)
                app.playing_media.append(media)
        return

    print(f"Playing local media ({media.name})...")
    media.play(app)
    return


@app.post("/stop/{media_id}")
def stop_media(media_id: int):
    selected_media = None
    for media in app.playing_media:
        if media.db_id == media_id:
            selected_media = media
            break

    if selected_media.client_id:
        client_obj = ClientObj.get_by_id(selected_media.client_id)
        print(f'Looking for client {client_obj.hostname}...')
        for cli_socket in app.client_sockets:
            if cli_socket.getpeername()[0] == client_obj.ip_address:
                message = MediaStopRequestMessage(selected_media.file_path)
                message.send(cli_socket)
                app.playing_media.remove(selected_media)
        return

    print(f"Stopping local media ({selected_media.name})...")
    selected_media.stop()
    app.playing_media.remove(selected_media)
    return


@app.put("/media/update")
def update_media(media_update: MediaUpdateRequest):
    media = Media.get_by_id(media_update.db_id)
    media.update(media_update.name, media_update.start_time, media_update.end_time)

    media = Media.get_by_id(media_update.db_id)
    return media


@app.post("/media/upload")
async def upload_media(file: UploadFile = File(...), client_id: int = Form(None)):
    file_obj = await file.read()
    print(type(file_obj))
    filename = file.filename
    if client_id:
        print(f'Uploading media to {client_id}...')
        client = ClientObj.get_by_id(client_id)

        files = {'file': (filename, file_obj)}
        receiver_url = f"http://{client.ip_address}:{settings.API_PORT}/media/upload"
        response = requests.post(receiver_url, files=files)
        return response.json()
    else:
        new_file = await Media.create(file_obj, filename)
        return new_file


@app.delete("/media/{media_id}")
def delete_media(media_id: int):
    media = Media.get_by_id(media_id)
    media.delete()

    if media.client_id:
        client_obj = ClientObj.get_by_id(media.client_id)
        print(f'Looking for client {client_obj.hostname}...')
        for cli_socket in app.client_sockets:
            if cli_socket.getpeername()[0] == client_obj.ip_address:
                delete_request = MediaDeleteRequestMessage(media)
                delete_request.send(cli_socket)

                return


@app.post("/cue")
def create_cue(cue_creation: CreateCueRequest):
    cue = Cue(name=cue_creation.name,
              source_media_id=cue_creation.sourceMediaId,
              source_media_timecode_secs=cue_creation.sourceMediaTimecode,
              target_media_id=cue_creation.targetMediaId)
    cue.insert_to_db()
    return cue


@app.put("/cue/update")
def update_cue(cue_update: CueUpdateRequest):
    cue = Cue.get_by_id(cue_update.db_id)
    cue.update(cue_update.name, cue_update.source_media_id, cue_update.source_media_timecode, cue_update.target_media_id, cue_update.is_enabled)

    cue = Cue.get_by_id(cue_update.db_id)
    return cue


@app.on_event("shutdown")
async def shutdown_event():
    print("STARTING SHUTDOWN...")
    # Set the stop flag to signal threads to stop
    app.stop_flag.set()

    print("CLOSING ACTIVE THREADS...")
    # Wait for threads to finish before exiting
    for thread in app.active_threads:
        print(f"CLOSING {thread}...")
        thread.join()

    print("READY FOR SHUTDOWN.")


def setup():
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    setup_server_db()

    connect_to_clients(app)


if __name__ == "__main__":
    setup()
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT, reload=False)

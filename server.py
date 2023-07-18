from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import requests
import socket
import sqlite3
import threading
import uvicorn

from pisync.lib.api.client_connect_request import ClientConnectRequest
from pisync.lib.api.client_search_response import Client as ApiClient, ClientSearchResponse
from pisync.lib.api.info_response import InfoResponse
from pisync.lib.api.media_update_request import MediaUpdateRequest
from pisync.lib.client import Client as ClientObj
from pisync.lib.media import Media

import settings


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    stored_media = Media.get_all_from_db()
    stored_clients = ClientObj.get_all_from_db()
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "existing_media": stored_media,
                                                     "existing_clients": stored_clients})


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
            result = sock.connect_ex((ip, settings.PORT))
            if result == 0:
                # Check the response body for 'is_client' == True
                response = requests.get(f"http://{ip}:{settings.PORT}/info")
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


def setup_db():
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

    # Define the Clients table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT UNIQUE,
        friendly_name TEXT UNIQUE,
        ip_address TEXT,
        is_online INTEGER
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


def handle_client(client_socket, client_address):
    print('Connected with client:', client_address)

    # Process client requests or send/receive data

    # Close the client connection
    client_socket.close()


def start_socket_server(server_socket):
    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()

        # Start a new thread to handle the client connection
        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )
        client_thread.start()


def connect_to_clients():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific IP address and port
    server_ip = '192.168.1.115'  # TODO remove hardcoded server IP
    server_socket.bind((server_ip, settings.PORT))

    # Listen for incoming connections
    server_socket.listen()

    print('Server listening on {}:{}'.format(server_ip, settings.PORT))

    # Start the socket server in a separate thread
    socket_thread = threading.Thread(target=start_socket_server, args=(server_socket,))
    socket_thread.start()

    clients = ClientObj.get_all_from_db()

    for client in clients:
        print(f'Attempting to connect to {client.hostname}...')
        try:
            resp = requests.get(f'http://{client.ip_address}:{settings.PORT}')
            client.update_online_status(resp.status_code == 200)
        except requests.exceptions.ConnectionError:
            client.update_online_status(False)


def setup():
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    setup_db()

    connect_to_clients()


if __name__ == "__main__":
    setup()
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)

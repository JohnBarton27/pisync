import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import requests
import socket
import threading
import uvicorn

from pisync.lib.api.client_connect_request import ClientConnectRequest
from pisync.lib.api.client_search_response import Client as ApiClient, ClientSearchResponse
from pisync.lib.api.create_cue_request import CreateCueRequest
from pisync.lib.api.info_response import InfoResponse
from pisync.lib.api.media_update_request import MediaUpdateRequest
from pisync.lib.client import Client as ClientObj
from pisync.lib.cue import Cue
from pisync.lib.media import Media
from pisync.lib.message import Message, ClientMediaDumpMessage, MediaPlayRequestMessage

import settings
from setup_db import setup_server_db


app = FastAPI()
app.state.db_name = 'pisync.db'
settings.APP_TYPE = 'server'
templates = Jinja2Templates(directory="templates")

# Threads
stop_flag = threading.Event()
active_threads = []

connected_clients = set()
client_sockets = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages from the client if needed
            pass
    except:
        connected_clients.remove(websocket)


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
        for cli_socket in client_sockets:
            if cli_socket.getpeername()[0] == client_obj.ip_address:
                message = MediaPlayRequestMessage(media.file_path)
                message.send(cli_socket)
        return

    print(f"Playing local media ({media.name})...")
    media.play(start_time=630, end_time=655)
    return


@app.put("/media/update")
def update_media(media_update: MediaUpdateRequest):
    media = Media.get_by_id(media_update.db_id)
    media.update_name(media_update.name)

    media = Media.get_by_id(media_update.db_id)
    return media


@app.post("/cue")
def create_cue(cue_creation: CreateCueRequest):
    cue = Cue(name=cue_creation.name,
              source_media_id=cue_creation.sourceMediaId,
              source_media_timecode_secs=cue_creation.sourceMediaTimecode,
              target_media_id=cue_creation.targetMediaId)
    cue.insert_to_db()
    return cue


async def tell_frontend_client_connection_event(client: ClientObj):
    for fe_client in connected_clients:
        await fe_client.send_text(json.dumps({'text': 'CLIENT CONNECTION EVENT', 'connected': client.is_online, 'ipAddress': client.ip_address, 'name': client.friendly_name}))


def receive_from_client(client_socket, client_address):
    print('Connected with client:', client_address)

    client_for_socket = ClientObj.get_by_ip_address(client_address[0])
    client_for_socket.update_online_status(True)

    asyncio.run(tell_frontend_client_connection_event(client_for_socket))

    client_socket.settimeout(1)
    client_socket.send('HELLO FROM THE SERVER'.encode())

    while not stop_flag.is_set():
        try:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                # Client disconnected
                print('Client disconnected:', client_address)
                client_for_socket.update_online_status(False)

                asyncio.run(tell_frontend_client_connection_event(client_for_socket))

                client_socket.close()
                break

            # Process received data
            message = Message.get_from_socket(data)

            if isinstance(message, ClientMediaDumpMessage):
                print(f'Received dump of media info from client at {client_address}')
                media_objs = message.get_content()
                Media.load_media_into_db_from_client(media_objs, client_for_socket.db_id)
            else:
                print(f'Received message from {client_address}')

        except ConnectionResetError:
            # Client forcibly closed the connection
            print('Client forcibly closed the connection:', client_address)
            client_for_socket.update_online_status(False)
            client_socket.close()
            break
        except socket.timeout:
            continue

    # Close the client connection
    client_socket.close()
    client_sockets.remove(client_socket)


def start_socket_server(server_socket):
    while not stop_flag.is_set():
        try:
            # Accept a client connection
            client_socket, client_address = server_socket.accept()
            client_sockets.append(client_socket)

            # Start a new thread to handle the client connection
            client_thread = threading.Thread(
                target=receive_from_client,
                args=(client_socket, client_address)
            )
            client_thread.start()
            active_threads.append(client_thread)
        except socket.timeout:
            continue

    server_socket.close()


def connect_to_clients():
    clients = ClientObj.get_all_from_db()

    # Start all clients as offline until they connect
    for client in clients:
        client.update_online_status(False)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO FOR DEV USE
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TODO END FOR DEV USE

    # Bind the socket to a specific IP address and port
    server_ip = '192.168.1.115'  # TODO remove hardcoded server IP
    server_socket.settimeout(1)
    server_socket.bind((server_ip, settings.SOCKET_PORT))

    # Listen for incoming connections
    server_socket.listen()

    print('Socket server listening on {}:{}'.format(server_ip, settings.SOCKET_PORT))

    # Start the socket server in a separate thread
    socket_thread = threading.Thread(target=start_socket_server, args=(server_socket,))
    socket_thread.start()
    active_threads.append(socket_thread)


@app.on_event("shutdown")
async def shutdown_event():
    print("STARTING SHUTDOWN...")
    # Set the stop flag to signal threads to stop
    stop_flag.set()

    print("CLOSING ACTIVE THREADS...")
    # Wait for threads to finish before exiting
    for thread in active_threads:
        print(f"CLOSING {thread}...")
        thread.join()

    print("READY FOR SHUTDOWN.")


def setup():
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    setup_server_db()

    connect_to_clients()


setup()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT, reload=False)

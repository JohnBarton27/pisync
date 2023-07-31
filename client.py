from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import socket
import threading
import time
import uvicorn

from pisync.lib.api.info_response import InfoResponse
from pisync.lib.media import Media
from pisync.lib.message import Message, ClientMediaDumpMessage, MediaPlayRequestMessage

from setup_db import setup_client_db
import settings

app = FastAPI()
settings.APP_TYPE = 'client'
templates = Jinja2Templates(directory="templates")

# Threads
stop_flag = threading.Event()
app.active_threads = []


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("client-index.html", {"request": request})


@app.get('/info')
def get_server_info():
    return InfoResponse(is_client=True)


@app.post("/play/{file_path}")
def play_media(file_path: int):
    media = Media.get_by_file_path(file_path)

    if media.client_id:
        raise Exception('This is a client - cannot play remote media!')

    print(f"Playing local media ({media.name})...")
    media.play()
    return


def connect_to_server():
    # Connect to the server
    server_ip = '192.168.1.115'  # TODO remove hardcoded server IP

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while not stop_flag.is_set():
        try:
            client_socket.connect((server_ip, settings.SOCKET_PORT))
            print('Connected to the server:', server_ip, settings.SOCKET_PORT)
            break
        except ConnectionRefusedError:
            print("Unable to hit server...")
            time.sleep(2)

    # Send Media objects to server
    media_objs = Media.get_all_from_db()
    media_pickle = pickle.dumps(media_objs)
    opening_message = ClientMediaDumpMessage(media_pickle)
    opening_message.send(client_socket)

    welcome_message = client_socket.recv(1024).decode()
    print(f"Server says: {welcome_message}")

    def receive_server_messages():
        while not stop_flag.is_set():
            data = client_socket.recv(1024)
            if not data:
                # Server disconnected
                print("Server disconnected.")
                client_socket.close()
                break

            message_obj = Message.get_from_socket(data)
            if isinstance(message_obj, MediaPlayRequestMessage):
                filepath_of_media_to_play = message_obj.get_content()
                for media in Media.get_all_from_db():
                    if media.file_path == filepath_of_media_to_play:
                        media.play()

    recv_thread = threading.Thread(target=receive_server_messages)
    recv_thread.start()
    app.active_threads.append(recv_thread)


@app.on_event("shutdown")
async def shutdown_event():
    stop_flag.is_set()

    for thread in app.active_threads:
        print(f"CLOSING {thread}...")
        thread.join()

    print("READY FOR SHUTDOWN.")


def setup():
    setup_client_db()

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    socket_thread = threading.Thread(target=connect_to_server)
    socket_thread.start()


if __name__ == "__main__":
    setup()
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)

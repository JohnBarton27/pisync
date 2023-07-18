from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socket
import threading
import time
import uvicorn

from pisync.lib.api.info_response import InfoResponse
import settings

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Threads
stop_flag = threading.Event()
active_threads = []


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("client-index.html", {"request": request})


@app.get('/info')
def get_server_info():
    return InfoResponse(is_client=True)


def connect_to_server():
    # Connect to the server
    server_ip = '192.168.1.115'  # TODO remove hardcoded server IP

    while not stop_flag.is_set():
        try:
            client_socket.connect((server_ip, settings.SOCKET_PORT))
            print('Connected to the server:', server_ip, settings.SOCKET_PORT)
            
            send_message('Hello, server!')

            # Continually receive data
            receive_thread = threading.Thread(target=receive_message)
            receive_thread.start()

            break
        except:
            print('Unable to hit server...')
            time.sleep(2)

    client_socket.close()


def send_message(message):
    # Send data to the server
    client_socket.send(message.encode())


def receive_message():
    while not stop_flag.is_set():
        # Receive data from the server
        data = client_socket.recv(1024)
        if not data:
            # Server disconnected
            print("Server disconnected.")
            client_socket.close()
            break
        print("Received message:", data.decode())

    # If disconnected, try to reconnect
    connect_to_server()


@app.on_event("shutdown")
async def shutdown_event():
    stop_flag.is_set()


def setup():
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    socket_thread = threading.Thread(target=connect_to_server)
    socket_thread.start()


if __name__ == "__main__":
    setup()
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)

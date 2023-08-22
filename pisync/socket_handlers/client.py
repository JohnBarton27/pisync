import asyncio
import pickle
import socket
import time

from pisync.lib.media import Media
from pisync.lib.message import (Message, ClientMediaDumpMessage, MediaPlayRequestMessage, MediaStopRequestMessage,
                                MediaIsPlayingMessage, MediaStatus)

import settings


async def play_media(media, client_socket, app):
    media_playing_message = MediaIsPlayingMessage(media, status=MediaStatus.PLAYING)
    media_playing_message.send(client_socket)
    media.play(app)
    media_stopped_message = MediaIsPlayingMessage(media, status=MediaStatus.STOPPED)
    media_stopped_message.send(client_socket)


def connect_to_server(app):
    # Connect to the server
    server_ip = '192.168.1.115'  # TODO remove hardcoded server IP

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while not app.stop_flag.is_set():
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

    def receive_server_messages():
        while not app.stop_flag.is_set():
            data = client_socket.recv(1024)
            if not data:
                # Server disconnected
                print("Server disconnected.")
                client_socket.close()
                break

            message_obj = Message.get_from_socket(data)
            if isinstance(message_obj, MediaPlayRequestMessage):
                print(f'Received message to play media...')
                filepath_of_media_to_play = message_obj.get_content()
                for media in Media.get_all_from_db():
                    if media.file_path == filepath_of_media_to_play:
                        asyncio.run(play_media(media, client_socket, app))
            elif isinstance(message_obj, MediaStopRequestMessage):
                print(f'Received message to stop playing media...')
                filepath_of_media_to_stop = message_obj.get_content()
                for media in Media.get_all_from_db():
                    if media.file_path == filepath_of_media_to_stop:
                        media.stop()

    receive_server_messages()

    # We disconnected - try connecting to the server again
    connect_to_server(app)

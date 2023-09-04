import asyncio
import json
import pickle
import socket
import threading

from pisync.lib.client import Client as ClientObj
from pisync.lib.media import Media, MediaStatus
from pisync.lib.message import Message, ClientMediaDumpMessage, MediaIsPlayingMessage

import settings


def connect_to_clients(app):
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
    socket_thread = threading.Thread(target=start_socket_server, args=(server_socket, app))
    socket_thread.start()
    app.active_threads.append(socket_thread)


def start_socket_server(server_socket, app):
    while not app.stop_flag.is_set():
        try:
            # Accept a client connection
            client_socket, client_address = server_socket.accept()
            app.client_sockets.append(client_socket)

            # Start a new thread to handle the client connection
            client_thread = threading.Thread(
                target=receive_from_client,
                args=(client_socket, client_address, app)
            )
            client_thread.start()
            app.active_threads.append(client_thread)
        except socket.timeout:
            continue

    server_socket.close()


def receive_from_client(client_socket, client_address, app):
    print('Connected with client:', client_address)

    client_for_socket = ClientObj.get_by_ip_address(client_address[0])
    client_for_socket.update_online_status(True)

    asyncio.run(tell_frontend_client_connection_event(client_for_socket, app))

    client_socket.settimeout(1)

    while not app.stop_flag.is_set():
        try:
            # Receive data from the client
            data = client_socket.recv(4096)

            if not data:
                # Client disconnected
                print('Client disconnected:', client_address)
                client_for_socket.update_online_status(False)

                asyncio.run(tell_frontend_client_connection_event(client_for_socket, app))

                client_socket.close()
                break

            # Process received data
            message = Message.get_from_socket(data)

            if isinstance(message, ClientMediaDumpMessage):
                print(f'Received dump of media info from client at {client_address}')
                media_objs = message.get_content()
                Media.load_media_into_db_from_client(media_objs, client_for_socket.db_id)
                fe_message = ClientMediaDumpMessage(pickle.dumps(Media.get_all_from_db()))
                asyncio.run(tell_frontend_client_media_dump(fe_message, app))
            elif isinstance(message, MediaIsPlayingMessage):
                print(f'Received MediaIsPlayingMessage from client at {client_address}')
                media_fp = message.media.file_path
                media = Media.get_by_file_path(media_fp)
                status = message.status
                asyncio.run(tell_frontend_client_media_status(media, status, app))
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
    app.client_sockets.remove(client_socket)


async def tell_frontend_client_connection_event(client: ClientObj, app):
    for fe_client in app.connected_clients:
        message_dict = {
            'text': 'CLIENT CONNECTION EVENT',
            'connected': client.is_online,
            'ipAddress': client.ip_address,
            'name': client.friendly_name
        }
        await fe_client.send_text(json.dumps(message_dict))


async def tell_frontend_client_media_status(media: Media, status: MediaStatus, app):
    message = MediaIsPlayingMessage(media, status)
    content = message.get_dict_content()

    for fe_client in app.connected_clients:
        await fe_client.send_text(json.dumps(content))


async def tell_frontend_client_media_dump(message: ClientMediaDumpMessage, app):
    content = message.get_dict_content()

    for fe_client in app.connected_clients:
        await fe_client.send_text(json.dumps(content))

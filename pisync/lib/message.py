import pickle
import socket


class Message:

    def __init__(self, msg_socket: socket, content, topic: str):
        self.content = content
        self.topic = topic
        self.socket = msg_socket

    def __str__(self):
        return f'{self.topic} | {self.content}'

    def send(self):
        message = pickle.dumps(self)
        print(f'Sending {message}...')
        self.socket.send(message)


class ClientMediaDumpMessage(Message):

    def __init__(self, msg_socket: socket, content):
        super().__init__(msg_socket, content, "ClientMediaDumpMessage")

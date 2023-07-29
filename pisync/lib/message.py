import pickle
import socket


class Message:

    def __init__(self, content, topic: str):
        self.content = content
        self.topic = topic

    def __str__(self):
        return f'{self.topic} | {self.content}'

    def send(self, msg_socket: socket):
        message = pickle.dumps(self)
        print(f'Sending {message}...')
        msg_socket.send(message)


class ClientMediaDumpMessage(Message):

    def __init__(self, content):
        super().__init__(content, "ClientMediaDumpMessage")

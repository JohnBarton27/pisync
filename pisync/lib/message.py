from fastapi import UploadFile
import pickle
import socket

from pisync.lib.media import Media, MediaStatus


class Message:

    def __init__(self, content, topic: str):
        self.content = content
        self.topic = topic

    def __str__(self):
        return f'{self.topic} | {self.content}'

    def send(self, msg_socket: socket):
        message = pickle.dumps(self)
        print(f'Sending {self.__class__.__name__} to {msg_socket.getpeername()[0]}...')
        msg_socket.send(message)

    @classmethod
    def get_from_socket(cls, data):
        message = pickle.loads(data)
        return message

    def get_content(self):
        return pickle.loads(self.content)


class ClientMediaDumpMessage(Message):

    def __init__(self, content):
        super().__init__(content, "ClientMediaDumpMessage")


class MediaPlayRequestMessage(Message):

    def __init__(self, content):
        """
        Message the server sends to a client to request the client play a media file

        :param content: Filepath to the Media File to be played
        """
        super().__init__(content, "MediaPlayRequestMessage")

    def get_content(self):
        return self.content


class MediaStopRequestMessage(Message):

    def __init__(self, content):
        """
        Message the server sends to a client to request the client stop playing a media file

        :param content: Filepath to the Media File to be stopped
        """
        super().__init__(content, "MediaPlayRequestMessage")

    def get_content(self):
        return self.content


class MediaIsPlayingMessage(Message):

    def __init__(self, media: Media, status: MediaStatus):
        """
        Message the server sends to the UI to indicate the current 'playing' status of a given piece of media.

        :param media: Media object whose status is being reported
        :param status: MediaStatus of the given Media object (STOPPED, PLAYING, etc.)
        """
        self.media = media
        self.status = status
        content = {
            'media': self.media,
            'status': self.status
        }
        super().__init__(content, "MediaIsPlayingMessage")

    def get_dict_content(self):
        return {
            'topic': self.topic,
            'content': {
                'media_id': self.media.db_id,
                'status': self.status.value
            }
        }


class MediaDeleteRequestMessage(Message):

    def __init__(self, media: Media):
        """
        Message the server sends to a client to request a media element be deleted.

        :param media: Media object to be deleted
        """
        self.media = media
        content = {
            'media': self.media
        }
        super().__init__(content, "MediaDeleteRequestMessage")


class MediaUploadRequestMessage(Message):

    def __init__(self, file: bytes, filename: str):
        """
        Message the server sends to a client to upload a file to the client.

        :param file: Media file to upload to the client
        """
        self.file = file
        self.filename = filename
        content = {
            'file': self.file,
            'name': self.filename
        }
        super().__init__(content, 'MediaUploadRequestMessage')

    def send(self, msg_socket: socket):
        import time
        print(f'Sending {self.__class__.__name__} to {msg_socket.getpeername()[0]}...')
        message = pickle.dumps(self)

        chunk_size = 4096
        total_chunks = (len(message) + chunk_size - 1) // chunk_size

        for i in range(0, len(message), chunk_size):
            time.sleep(1)
            chunk = message[i:i+chunk_size]
            msg_socket.send(chunk)
            print(f"Sent chunk {i//chunk_size + 1}/{total_chunks}")

        msg_socket.send(message)

        # Let the client know we are done sending!
        complete_message = MediaUploadCompleteMessage()
        complete_message.send(msg_socket)


class MediaUploadCompleteMessage(Message):

    def __init__(self):
        """
        Server lets the client know that the file transfer is complete & has no more pieces to send!
        """
        super().__init__({}, 'MediaUploadCompleteMessage')

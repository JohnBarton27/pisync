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
        print(f'Sending {message}...')
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

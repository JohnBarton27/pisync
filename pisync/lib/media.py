from abc import ABC, abstractmethod
from enum import Enum
import os
from pydantic import BaseModel
import sqlite3
from typing import Optional

from pisync.lib.client import Client
import settings


class MediaTypes(Enum):

    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'


class Media(BaseModel, ABC):
    file_path: str = None
    name: str = None
    db_id: int = None
    client_id: Optional[int] = None

    @abstractmethod
    def play(self, start_time: int = 0, end_time: int = None):
        pass

    @property
    def client(self):
        if not self.client_id:
            return None

        return Client.get_by_id(self.client_id)

    def exists_in_database(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        if not self.client_id:
            select_query = "SELECT file_path FROM media WHERE file_path = ? AND client_id IS NULL"
            cursor.execute(select_query, (self.file_path,))
        else:
            select_query = "SELECT file_path FROM media WHERE file_path = ? AND client_id = ?"
            cursor.execute(select_query, (self.file_path, self.client_id))

        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_to_db(self):
        from pisync.lib.audio import Audio
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        insert_query = "INSERT INTO media (file_path, file_name, file_type, client_id) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_query, (self.file_path, self.name, MediaTypes.AUDIO.value if isinstance(self, Audio) else MediaTypes.VIDEO.value, self.client_id))
        conn.commit()
        conn.close()

    @classmethod
    def load_media_into_db_from_client(cls, client_media: list, source_client_id: int):
        for media in client_media:
            media.client_id = source_client_id
            if not media.exists_in_database():
                media.insert_to_db()

            # TODO handle name updates/etc.

    def update_name(self, new_name: str):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE media SET file_name = ? WHERE id = ?"
        cursor.execute(update_query, (new_name, self.db_id))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, db_id: int):
        for media in cls.get_all_from_db():
            if media.db_id == db_id:
                return media

        return None

    @classmethod
    def get_by_file_path(cls, file_path: str):
        # TODO switch to SQL SELECT
        for media in cls.get_all_from_db():
            if media.file_path == file_path:
                return media

        return None

    @classmethod
    def get_all_from_db(cls):
        conn = cls.get_db_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        select_query = "SELECT * FROM media"
        cursor.execute(select_query)
        results = cursor.fetchall()

        medias = []
        for result in results:
            medias.append(cls.get_from_db_result(result))

        return medias

    @classmethod
    def get_from_db_result(cls, result):
        from pisync.lib.audio import Audio
        from pisync.lib.video import Video

        file_path = result['file_path']
        name = result['file_name']
        db_id = result['id']
        file_type = MediaTypes.AUDIO if result['file_type'] == MediaTypes.AUDIO.value else MediaTypes.VIDEO
        client_id = result['client_id']

        if file_type == MediaTypes.AUDIO:
            return Audio(file_path=file_path, name=name, db_id=db_id, client_id=client_id)
        elif file_type == MediaTypes.VIDEO:
            return Video(file_path=file_path, name=name, db_id=db_id, client_id=client_id)

    @classmethod
    def get_db_conn(cls):
        if settings.APP_TYPE == 'client':
            database_file = "pisync_client.db"
        else:
            database_file = "pisync.db"
        return sqlite3.connect(database_file)

    @classmethod
    def get_all_local_files(cls):
        from pisync.lib.audio import Audio
        from pisync.lib.video import Video

        media_dir = os.path.join(os.getcwd(), 'media')
        file_list = []

        for file_name in os.listdir(media_dir):
            file_path = os.path.join(media_dir, file_name)

            if os.path.isfile(file_path):
                file_type = cls.get_file_type(file_name)

                if file_type == MediaTypes.AUDIO:
                    file_list.append(Audio(file_path=file_path, name=file_path))
                elif file_type == MediaTypes.VIDEO:
                    file_list.append(Video(file_path=file_path, name=file_path))

        return file_list

    @staticmethod
    def get_file_type(file_name):
        audio_extensions = ['.mp3', '.wav', '.aac']
        video_extensions = ['.mp4', '.mov', '.avi']

        _, file_extension = os.path.splitext(file_name)

        if file_extension in audio_extensions:
            return MediaTypes.AUDIO
        elif file_extension in video_extensions:
            return MediaTypes.VIDEO
        else:
            return None

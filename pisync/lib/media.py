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


class MediaStatus(Enum):

    STOPPED = 'STOPPED'
    PLAYING = 'PLAYING'
    PAUSED = 'PAUSED'


class Media(BaseModel, ABC):
    file_path: str = None
    name: str = None
    db_id: int = None
    client_id: Optional[int] = None
    start_timecode: Optional[float] = None
    end_timecode: Optional[float] = None
    stop_signal: bool = False

    @abstractmethod
    def play(self, app):
        pass

    @property
    def client(self):
        if not self.client_id:
            return None

        return Client.get_by_id(self.client_id)

    def stop(self):
        self.stop_signal = True

    def exists_in_database(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        if not self.client_id:
            select_query = "SELECT file_path FROM media WHERE file_path = ? AND client_id IS NULL"
            select_params = (self.file_path,)
        else:
            select_query = "SELECT file_path FROM media WHERE file_path = ? AND client_id = ?"
            select_params = (self.file_path, self.client_id)

        cursor.execute(select_query, select_params)

        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_to_db(self):
        from pisync.lib.audio import Audio
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        insert_query = "INSERT INTO media (file_path, file_name, file_type, client_id, start_timecode, end_timecode) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (self.file_path,
                                      self.name,
                                      MediaTypes.AUDIO.value if isinstance(self, Audio) else MediaTypes.VIDEO.value,
                                      self.client_id,
                                      self.start_timecode,
                                      self.end_timecode))
        self.db_id = cursor.lastrowid

        conn.commit()
        conn.close()

    @classmethod
    def load_media_into_db_from_client(cls, client_media: list, source_client_id: int):
        for media in client_media:
            media.client_id = source_client_id
            if not media.exists_in_database():
                media.insert_to_db()

            # TODO handle name updates/etc.

    @classmethod
    async def create(cls, file: bytes, name: str):
        media_dir = os.path.join(os.getcwd(), 'media')
        upload_destination = os.path.join(media_dir, name)

        with open(upload_destination, "wb") as new_file:
            new_file.write(file)

        Media.update_db_with_local_files()
        return cls.get_by_file_path(upload_destination)

    def update(self, new_name: str, new_start_time: float, new_end_time: float):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE media SET file_name = ?, start_timecode = ?, end_timecode = ? WHERE id = ?"
        cursor.execute(update_query, (new_name, new_start_time, new_end_time, self.db_id))
        conn.commit()
        conn.close()

    def delete(self, remove_related_cues: bool = True):
        if not self.client_id:
            # Local media, delete from disk!
            os.remove(self.file_path)
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        if remove_related_cues:
            # Remove any cues this piece of media was used in (should always be done when deleting from server)
            from pisync.lib.cue import Cue
            for cue in Cue.get_all_from_db():
                # TODO update Media's __eq__ and __hash__ to make this comparison easier
                if self.db_id in [cue.target_media.db_id, cue.source_media_id]:
                    cue.delete()

        # Delete actual media element
        delete_query = "DELETE from media WHERE id = ?"
        cursor.execute(delete_query, (self.db_id,))
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

        file_type = MediaTypes.AUDIO if result['file_type'] == MediaTypes.AUDIO.value else MediaTypes.VIDEO

        common_args = {
            "file_path": result['file_path'],
            "name": result['file_name'],
            "db_id": result['id'],
            "client_id": result['client_id'],
            "start_timecode": result['start_timecode'],
            "end_timecode": result['end_timecode']
        }

        if file_type == MediaTypes.AUDIO:
            return Audio(**common_args)
        elif file_type == MediaTypes.VIDEO:
            return Video(**common_args)

    @classmethod
    def get_db_conn(cls):
        if settings.APP_TYPE == 'client':
            database_file = "pisync_client.db"
        else:
            database_file = "pisync.db"
        return sqlite3.connect(database_file)

    @classmethod
    def update_db_with_local_files(cls):
        media_files = cls.get_all_local_files()

        # Check if each file exists in the database, and if not, add it
        for media in media_files:
            if not media.exists_in_database():
                media.insert_to_db()

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

                common_args = {
                    "file_path": file_path,
                    "name": file_path
                }

                if file_type == MediaTypes.AUDIO:
                    file_list.append(Audio(**common_args))
                elif file_type == MediaTypes.VIDEO:
                    file_list.append(Video(**common_args))

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

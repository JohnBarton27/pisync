from abc import ABC, abstractmethod
from enum import Enum
import os
from pydantic import BaseModel
import sqlite3


class MediaTypes(Enum):

    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'


class Media(BaseModel, ABC):
    file_path: str = None
    name: str = None
    db_id: int = None

    @abstractmethod
    def play(self, start_time: int = 0, end_time: int = None):
        pass

    def exists_in_database(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        select_query = "SELECT file_path FROM media WHERE file_path = ?"
        cursor.execute(select_query, (self.file_path,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_to_db(self):
        from pisync.lib.audio import Audio
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        insert_query = "INSERT INTO media (file_path, file_name, file_type) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (self.file_path, self.name, MediaTypes.AUDIO.value if isinstance(self, Audio) else MediaTypes.VIDEO.value))
        conn.commit()
        conn.close()

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
        file_path = result['file_path']
        name = result['file_name']
        db_id = result['id']
        file_type = MediaTypes.AUDIO if result['file_type'] == MediaTypes.AUDIO.value else MediaTypes.VIDEO

        if file_type == MediaTypes.AUDIO:
            return Audio(file_path=file_path, name=name, db_id=db_id)
        elif file_type == MediaTypes.VIDEO:
            print('VIDEO NOT YET SUPPORTED')

    @classmethod
    def get_db_conn(cls):
        database_file = "pisync.db"
        return sqlite3.connect(database_file)

    @classmethod
    def get_all_files(cls):
        from pisync.lib.audio import Audio
        media_dir = os.path.join(os.getcwd(), 'media')
        file_list = []

        for file_name in os.listdir(media_dir):
            file_path = os.path.join(media_dir, file_name)

            if os.path.isfile(file_path):
                file_type = cls.get_file_type(file_name)

                if file_type == MediaTypes.AUDIO:
                    file_list.append(Audio(file_path=file_path, name=file_path))
                elif file_type == MediaTypes.VIDEO:
                    print('VIDEO NOT YET SUPPORTED')

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

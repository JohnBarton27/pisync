import os
from pydantic import BaseModel
import sqlite3
from typing import Optional

from pisync.lib.media import Media
import settings


class Cue(BaseModel):
    name: str = None
    db_id: int = None
    source_media_id: int = None
    source_media_timecode_secs: int = None
    target_media_id: int = None

    @property
    def source_media(self):
        if not self.source_media_id:
            return None

        return Media.get_by_id(self.source_media_id)

    @property
    def target_media(self):
        if not self.target_media_id:
            return None

        return Media.get_by_id(self.target_media_id)

    def exists_in_database(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        select_query = "SELECT friendly_name FROM cues WHERE source_media_id = ? AND source_media_timecode_secs = ?"
        cursor.execute(select_query, (self.source_media_id, self.source_media_timecode_secs))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_to_db(self):
        from pisync.lib.audio import Audio
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        insert_query = "INSERT INTO cues (friendly_name, source_media_id, source_media_timecode_secs, target_media_id) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_query, (self.name, self.source_media_id, self.source_media_timecode_secs, self.target_media_id))
        conn.commit()
        conn.close()

    def update_name(self, new_name: str):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE cues SET friendly_name = ? WHERE id = ?"
        cursor.execute(update_query, (new_name, self.db_id))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, db_id: int):
        for cue in cls.get_all_from_db():
            if cue.db_id == db_id:
                return cue

        return None

    @classmethod
    def get_all_from_db(cls):
        conn = cls.get_db_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        select_query = "SELECT * FROM cues"
        cursor.execute(select_query)
        results = cursor.fetchall()

        cues = []
        for result in results:
            cues.append(cls.get_from_db_result(result))

        return cues

    @classmethod
    def get_from_db_result(cls, result):
        name = result['friendly_name']
        source_media_id = result['source_media_id']
        source_media_timecode_secs = result['source_media_timecode_secs']
        target_media_id = result['target_media_id']
        db_id = result['id']

        return Cue(name=name, db_id=db_id, source_media_id=source_media_id, source_media_timecode_secs=source_media_timecode_secs, target_media_id=target_media_id)

    @classmethod
    def get_db_conn(cls):
        if settings.APP_TYPE == 'client':
            database_file = "pisync_client.db"
        else:
            database_file = "pisync.db"
        return sqlite3.connect(database_file)

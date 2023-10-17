import os
from pydantic import BaseModel
import sqlite3
from typing import Optional

from pisync.lib.led_pattern import LedPattern
from pisync.lib.media import Media
import settings


class Cue(BaseModel):
    name: str = None
    db_id: int = None
    source_media_id: int = None
    source_media_timecode_secs: float = None
    target_media_id: int = None
    target_pattern_id: int = None
    is_enabled: bool = True

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

    @property
    def target_pattern(self):
        if not self.target_pattern_id:
            return None

        return LedPattern.get_by_id(self.target_pattern_id)

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

        insert_query = "INSERT INTO cues (friendly_name, source_media_id, source_media_timecode_secs, target_media_id, target_pattern_id) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (self.name, self.source_media_id, self.source_media_timecode_secs, self.target_media_id, self.target_pattern_id))
        self.db_id = cursor.lastrowid

        conn.commit()
        conn.close()

    def update(self, new_name: str, new_source_media_id: int, new_source_media_timecode: float, new_target_media_id: int, new_target_pattern_id: int, is_enabled: bool):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE cues SET friendly_name = ?, source_media_id = ?, source_media_timecode_secs = ?, target_media_id = ?, target_pattern_id = ?, is_enabled = ? WHERE id = ?"
        cursor.execute(update_query, (new_name, new_source_media_id, str(new_source_media_timecode), new_target_media_id, new_target_pattern_id, 1 if is_enabled else 0, self.db_id))
        conn.commit()
        conn.close()

    def delete(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        delete_query = "DELETE from cues WHERE id = ?"
        cursor.execute(delete_query, (self.db_id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, db_id: int):
        for cue in cls.get_all_from_db():
            if cue.db_id == db_id:
                return cue

        return None

    @classmethod
    def get_for_source_media(cls, src_media, include_disabled: bool = False):
        # TODO switch to SQL SELECT
        cues_to_watch_for = []
        for cue in cls.get_all_from_db():
            if cue.source_media_id == src_media.db_id and (include_disabled or cue.is_enabled):
                cues_to_watch_for.append(cue)

        return cues_to_watch_for

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
        target_pattern_id = result['target_pattern_id']
        db_id = result['id']
        is_enabled = bool(result['is_enabled'])

        return Cue(name=name, db_id=db_id, source_media_id=source_media_id, source_media_timecode_secs=source_media_timecode_secs, target_media_id=target_media_id, target_pattern_id=target_pattern_id, is_enabled=is_enabled)

    @classmethod
    def get_db_conn(cls):
        if settings.APP_TYPE == 'client':
            database_file = "pisync_client.db"
        else:
            database_file = "pisync.db"
        return sqlite3.connect(database_file)

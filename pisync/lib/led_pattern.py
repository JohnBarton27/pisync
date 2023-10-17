from pydantic import BaseModel
import sqlite3
from typing import Optional

from pisync.lib.client import Client
import settings


class LedPattern(BaseModel):
    name: str = None
    db_id: int = None
    client_id: Optional[int] = None

    def play(self):
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
            select_query = "SELECT name FROM ledPattern WHERE name = ? AND client_id IS NULL"
            select_params = (self.name,)
        else:
            select_query = "SELECT name FROM ledPattern WHERE name = ? AND client_id = ?"
            select_params = (self.name, self.client_id)

        cursor.execute(select_query, select_params)

        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_to_db(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        insert_query = "INSERT INTO ledPattern (name, client_id) VALUES (?, ?)"
        cursor.execute(insert_query, (self.name,
                                      self.client_id))
        self.db_id = cursor.lastrowid

        conn.commit()
        conn.close()

    def update(self, new_name: str):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE ledPattern SET name = ? WHERE id = ?"
        cursor.execute(update_query, (new_name, self.db_id))
        conn.commit()
        conn.close()

    def delete(self, remove_related_cues: bool = True):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        if remove_related_cues:
            # TODO REMOVE RELATED CUES
            pass

        # Delete actual media element
        delete_query = "DELETE from ledPattern WHERE id = ?"
        cursor.execute(delete_query, (self.db_id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, db_id: int):
        for led_pattern in cls.get_all_from_db():
            if led_pattern.db_id == db_id:
                return led_pattern

        return None

    @classmethod
    def get_all_from_db(cls):
        conn = cls.get_db_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        select_query = "SELECT * FROM ledPattern"
        cursor.execute(select_query)
        results = cursor.fetchall()

        medias = []
        for result in results:
            medias.append(cls.get_from_db_result(result))

        return medias

    @classmethod
    def get_for_client_id(cls, client_id: int):
        conn = cls.get_db_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        select_query = "SELECT * FROM ledPattern WHERE client_id = ?;"
        cursor.execute(select_query, (client_id,))
        results = cursor.fetchall()

        medias = []
        for result in results:
            medias.append(cls.get_from_db_result(result))

        return medias

    @classmethod
    def get_from_db_result(cls, result):
        return LedPattern(name=result['name'], client_id=result['client_id'],)

    @classmethod
    def get_db_conn(cls):
        if settings.APP_TYPE == 'client':
            database_file = "pisync_client.db"
        else:
            database_file = "pisync.db"
        return sqlite3.connect(database_file)

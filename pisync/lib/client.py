from pydantic import BaseModel

import sqlite3


class Client(BaseModel):
    hostname: str = None
    friendly_name: str = None
    ip_address: str = None
    is_online: bool = False
    db_id: int = None

    def __eq__(self, other):
        if not isinstance(other, Client):
            return False

        return self.hostname == other.hostname

    def __hash__(self):
        return hash(self.hostname)

    def exists_in_database(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        select_query = "SELECT hostname FROM clients WHERE host_name = ?"
        cursor.execute(select_query, (self.hostname,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def insert_to_db(self):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()

        insert_query = "INSERT INTO clients (hostname, friendly_name, ip_address, is_online) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_query, (self.hostname, self.friendly_name, self.ip_address, 1 if self.is_online else 0))
        self.db_id = cursor.lastrowid

        conn.commit()
        conn.close()

    def update_friendly_name(self, new_name: str):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE clients SET friendly_name = ? WHERE id = ?"
        cursor.execute(update_query, (new_name, self.db_id))
        conn.commit()
        conn.close()

        self.friendly_name = new_name

    def update_ip_address(self, new_ip_address: str):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE clients SET ip_address = ? WHERE id = ?"
        cursor.execute(update_query, (new_ip_address, self.db_id))
        conn.commit()
        conn.close()

        self.ip_address = new_ip_address

    def update_online_status(self, is_online: bool):
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        update_query = "UPDATE clients SET is_online = ? WHERE id = ?"
        cursor.execute(update_query, (1 if is_online else 0, self.db_id))
        conn.commit()
        conn.close()

        self.is_online = is_online

    def delete(self):
        # Import here to avoid circular import
        from pisync.lib.media import Media

        # Delete all media this client held
        for media in Media.get_for_client_id(self.db_id):
            media.delete(remove_related_cues=True)

        # Delete the client itself from the DB
        conn = self.__class__.get_db_conn()
        cursor = conn.cursor()
        delete_query = "DELETE from clients WHERE id = ?"
        cursor.execute(delete_query, (self.db_id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, db_id: int):
        for client in cls.get_all_from_db():
            if client.db_id == db_id:
                return client

        return None

    @classmethod
    def get_by_ip_address(cls, ip_address: str):
        for client in cls.get_all_from_db():
            if client.ip_address == ip_address:
                return client

        return None

    @classmethod
    def get_all_from_db(cls):
        conn = cls.get_db_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        select_query = "SELECT * FROM clients"
        cursor.execute(select_query)
        results = cursor.fetchall()

        clients = []
        for result in results:
            clients.append(cls.get_from_db_result(result))

        return clients

    @classmethod
    def get_from_db_result(cls, result):
        friendly_name = result['friendly_name']
        hostname = result['hostname']
        ip_address = result['ip_address']
        db_id = result['id']

        return Client(friendly_name=friendly_name,
                      ip_address=ip_address,
                      hostname=hostname,
                      db_id=db_id,
                      is_online=bool(result['is_online']))

    @classmethod
    def get_db_conn(cls):
        database_file = "pisync.db"
        return sqlite3.connect(database_file)

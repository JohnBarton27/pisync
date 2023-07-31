import os
import sqlite3


def setup_media_table(cursor):
    # Define the Media table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        file_name TEXT UNIQUE,
        file_type TEXT,
        client_id INTEGER
    )
    """
    cursor.execute(create_table_query)

    # Create the 'media' folder if it doesn't exist
    media_dir = os.path.join(os.getcwd(), 'media')
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Find all media files in the 'media' folder
    from pisync.lib.media import Media
    media_files = Media.get_all_local_files()

    # Check if each file exists in the database, and if not, add it
    for media in media_files:
        if not media.exists_in_database():
            media.insert_to_db()


def setup_server_db():
    # Setup DB
    database_file = 'pisync.db'
    db_conn = sqlite3.connect(database_file)
    db_cursor = db_conn.cursor()

    setup_media_table(db_cursor)

    # Define the Clients table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT UNIQUE,
        friendly_name TEXT UNIQUE,
        ip_address TEXT,
        is_online INTEGER
    )
    """
    db_cursor.execute(create_table_query)

    # Define the Cues table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        friendly_name TEXT UNIQUE,
        source_media_id INT NOT NULL,
        source_media_timecode_secs REAL NOT NULL,
        target_media_id INT
    )
    """
    db_cursor.execute(create_table_query)

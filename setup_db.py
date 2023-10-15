import os
import sqlite3


def setup_media_table(cursor, is_server: bool):
    """
    Creates the 'media' table in the database and populates it with any found local media

    :param cursor: Database cursor - used to execute SQL commands against the proper DB
    :param is_server: bool - if True, adds the 'client_id' field to the database
    :return: None
    """
    # Define the Media table
    column_defs = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        file_name TEXT UNIQUE,
        file_type TEXT,
        start_timecode REAL,
        end_timecode REAL,
        client_id INTEGER
    """

    if is_server:
        column_defs = f"""
            {column_defs},
            client_id INTEGER
        """

    create_media_table_query = f"""
    CREATE TABLE IF NOT EXISTS media (
        {column_defs}
    )
    """

    cursor.execute(create_media_table_query)

    # Create the 'media' folder if it doesn't exist
    media_dir = os.path.join(os.getcwd(), 'media')
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Find all media files in the 'media' folder
    from pisync.lib.media import Media
    Media.update_db_with_local_files()


def setup_server_db():
    # Setup DB
    database_file = 'pisync.db'
    db_conn = sqlite3.connect(database_file)
    db_cursor = db_conn.cursor()

    setup_media_table(db_cursor, is_server=True)

    # Define the Clients table
    create_client_table_query = """
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT UNIQUE,
        friendly_name TEXT UNIQUE,
        ip_address TEXT,
        is_online INTEGER
    )
    """
    db_cursor.execute(create_client_table_query)

    # Define the LED Pattern table
    create_led_table_query = """
    CREATE TABLE IF NOT EXISTS ledPattern (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        name TEXT
    )
    """
    db_cursor.execute(create_led_table_query)

    # Define the Cues table
    create_cue_table_query = """
    CREATE TABLE IF NOT EXISTS cues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        friendly_name TEXT UNIQUE,
        source_media_id INT NOT NULL,
        source_media_timecode_secs REAL NOT NULL,
        target_media_id INT,
        is_enabled INTEGER NOT NULL DEFAULT 1
    )
    """
    db_cursor.execute(create_cue_table_query)


def setup_client_db():
    # Setup DB
    database_file = 'pisync_client.db'
    db_conn = sqlite3.connect(database_file)
    db_cursor = db_conn.cursor()

    setup_media_table(db_cursor, is_server=False)

    # Define the LED Pattern table
    create_led_table_query = """
    CREATE TABLE IF NOT EXISTS ledPattern (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """
    db_cursor.execute(create_led_table_query)

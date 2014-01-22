import sqlite3
import collections
import os


class Database:
    def __init__(self, file_path='../build/database.db'):
        self.file_path = file_path
        self.connection = None

    def truncate_db(self):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
        self.create_tables()

    def get_connection(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.file_path)
            self.connection.text_factory = str
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def create_tables(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tracks
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, trackno INTEGER, title TEXT,
                             album_title TEXT, album_artist TEXT)
        """)
        connection.commit()

    def insert(self, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.executemany("INSERT INTO tracks (file_path, trackno, title, album_title, album_artist) "
                           "VALUES (?, ?, ?, ?, ?)", values)
        connection.commit()

    def get_file_path(self, music_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT file_path FROM tracks WHERE id = %s" % music_id)

        return cursor.fetchone()[0]

    def list(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tracks ORDER BY album_title, trackno, title, album_artist ASC")

        rows = []
        for db_row in cursor.fetchall():
            row = collections.OrderedDict()
            for db_col in db_row.keys():
                row[db_col] = db_row[db_col]
            rows.append(row)
        return rows

#['title', 'caption', 'comment', 'size', 'type', 'subtype', 'timestamp', 'keywords', 'country', 'language', 'langcode',
# 'url', 'media', 'artist', 'mime', 'datetime', 'tags', 'hash', 'channels', 'samplerate', 'length', 'encoder', 'codec',
# 'format', 'samplebits', 'bitrate', 'fourcc', 'trackno', 'id', 'userdate', 'enabled', 'default', 'codec_private',
# 'trackof', 'album', 'genre', 'discs', 'thumbnail', 'composer', 'mode']

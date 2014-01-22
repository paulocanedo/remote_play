import os, sqlite3, kaa

class MusicFinder:
    def __init__(self):
        self.music = "/home/paulocanedo/Music"
        self.database_path = 'database.db'
        self.connection = sqlite3.connect(self.database_path)

    def create_database(self):
        files = self.list_files()

        cursor = self.connenction.cursor()

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS track
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, filepath TEXT, number INTEGER, title TEXT, album_title TEXT, album_artist TEXT)
        """)
        self.connection.commit()

        finder = MusicFinder()
        musics = finder.list_files()
        musics_mdata = []

        for music in musics:
            mdata = kaa.metadata.parse(music)
            if mdata:
                values = (repr(music), mdata.get('trackno'), mdata.get('title'), mdata.get('album'), mdata.get('artist'))
                musics_mdata.append(values)

        cursor.executemany("INSERT INTO track (filepath, number, title, album_title, album_artist) VALUES (?, ?, ?, ?, ?)", musics_mdata)
        self.connection.commit()
        print "database created"

    def list_files(self):
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM track")
        rows = cursor.fetchall()

        return rows

    def list_file_from_filesystem(self):
        file_list = []

        extensions = {".mp3", ".m4a", ".flac"}

        for root, subFolders, files in os.walk(self.music):
            for f in files:
                for extension in extensions:
                    if f.endswith(extension):
                        file_list.append(os.path.join(root, f))
        return file_list
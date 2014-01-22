import sqlite3, kaa.metadata, os

class MusicFinder:
    def __init__(self):
        self.music = "/home/paulocanedo/Downloads/Music"
        self.fileList = []

    def list_files(self):
        del self.fileList[:]

        extensions = {".mp3"}

        for root, subFolders, files in os.walk(self.music):
            for file in files:
                for extension in extensions:
                    if (file.endswith(extension)):
                        self.fileList.append(os.path.join(root, file))
        return self.fileList

conn = sqlite3.connect("database.db")
conn.text_factory = str
cursor = conn.cursor()

cursor.execute("""
                CREATE TABLE IF NOT EXISTS track
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, filepath TEXT, number INTEGER, title TEXT, album_title TEXT, album_artist TEXT)
""")

conn.commit()

finder = MusicFinder()
musics = finder.list_files()
musics_mdata = []

for music in musics:
    mdata = kaa.metadata.parse(music)
    if mdata:
        values = (str(music), mdata.get('trackno'), mdata.get('title'), mdata.get('album'), mdata.get('artist'))
        musics_mdata.append(values)

cursor.executemany("INSERT INTO track (filepath, number, title, album_title, album_artist) VALUES (?, ?, ?, ?, ?)", musics_mdata)
conn.commit()
print "database created"

#['title', 'caption', 'comment', 'size', 'type', 'subtype', 'timestamp', 'keywords', 'country', 'language', 'langcode', 'url', 'media', 'artist', 'mime', 'datetime', 'tags', 'hash', 'channels', 'samplerate', 'length', 'encoder', 'codec', 'format', 'samplebits', 'bitrate', 'fourcc', 'trackno', 'id', 'userdate', 'enabled', 'default', 'codec_private', 'trackof', 'album', 'genre', 'discs', 'thumbnail', 'composer', 'mode']

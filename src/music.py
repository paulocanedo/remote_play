import os
import kaa.metadata
from database import Database


class MusicFinder:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.database = Database()
        self.rebuild = True

    def list_musics(self):
        if self.rebuild:
            base_dir = self.base_dir
            values = MusicFinder.list_musics_from_filesystem(base_dir)
            self.database.truncate_db()
            self.database.insert(values)
            self.rebuild = False
        return self.list_musics_from_database()

    def list_musics_from_database(self):
        return self.database.list()

    def get_file_path(self, music_id):
        return self.database.get_file_path(music_id)

    @staticmethod
    def list_musics_from_filesystem(base_dir):
        files = MusicFinder.list_files_from_filesystem(base_dir)
        musics_mdata = []
        for f in files:
            mdata = kaa.metadata.parse(f)
            if mdata:
                values = (str(f), mdata.get('trackno'), mdata.get('title'), mdata.get('album'), mdata.get('artist'))
                musics_mdata.append(values)

        return musics_mdata

    @staticmethod
    def list_files_from_filesystem(base_dir, extensions={".mp3", ".flac"}):
        file_list = []

        for root, subFolders, files in os.walk(base_dir):
            for f in files:
                for extension in extensions:
                    if f.endswith(extension):
                        path = os.path.join(root, f)
                        file_list.append(path)
        return file_list
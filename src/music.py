import os
import pygame
import kaa.metadata
from database import Database


class MusicFinder:
    def __init__(self, base_dir):
        self._base_dir = base_dir
        self._database = Database()
        self._rebuild = True

    def list_musics(self):
        if self._rebuild:
            base_dir = self._base_dir
            values = MusicFinder.list_musics_from_filesystem(base_dir)
            self._database.truncate_db()
            self._database.insert(values)
            self._rebuild = False
        return self.list_musics_from_database()

    def list_musics_from_database(self):
        return self._database.list()

    def get_metadata(self, music_id):
        return self._database.get_one(music_id)

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


class MusicPlayer:

    def __init__(self, finder):
        self._finder = finder
        self._current_music = None

    def play_next(self):
        return True

    def play_prev(self):
        return True

    def current_title(self):
        return 'not_playing' if not self._current_music else self._current_music[2]

    def play(self, music_id):
        self._current_music = self._finder.get_metadata(music_id)
        file_path = self._current_music[0]

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()

    def get_volume(self):
        return pygame.mixer.music.get_volume()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def get_position(self):
        return pygame.mixer.music.get_pos()

    def set_position(self, position):
        pygame.mixer.music.set_pos(position)

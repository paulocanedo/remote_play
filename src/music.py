import os
import pygame
import time
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from threading import Thread
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
    def read_metadata(file_path):
        if file_path.endswith(".mp3"):
            return MusicFinder.read_metadata_mp3(file_path)
        elif file_path.endswith(".m4a"):
            return MusicFinder.read_metadata_m4a(file_path)
        return None

    @staticmethod
    def read_metadata_mp3(file_path):
        # ['date', 'performer', 'tracknumber', 'album', 'genre', 'artist', 'title', 'bpm', 'albumsort']
        mdata = MP3(file_path, ID3=EasyID3)
        if mdata:
            values = (str(file_path),
                      MusicFinder.__get_value(mdata, "tracknumber"),
                      mdata.info.length * 1000,
                      MusicFinder.__get_value(mdata, "title"),
                      MusicFinder.__get_value(mdata, "album"),
                      MusicFinder.__get_value(mdata, "artist"))

            return values

        return None

    @staticmethod
    def read_metadata_m4a(file_path):
        mdata = MP4(file_path)
        if mdata:
            values = (str(file_path),
                      str(MusicFinder.__get_value(mdata, "trkn")),
                      MusicFinder.__get_value(mdata, "\xa9nam"),
                      MusicFinder.__get_value(mdata, "\xa9alb"),
                      MusicFinder.__get_value(mdata, "\xa9ART"))

            return values

        return None

    @staticmethod
    def list_musics_from_filesystem(base_dir):
        files = MusicFinder.list_files_from_filesystem(base_dir)
        musics_mdata = []
        for f in files:
            mdata = MusicFinder.read_metadata(f)
            if mdata:
                musics_mdata.append(mdata)

        return musics_mdata

    @staticmethod
    def __get_value(mdata, key):
        return mdata.get(key)[0] if key in mdata.keys() else None

    @staticmethod
    def list_files_from_filesystem(base_dir, extensions={".mp3"}):
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
        self._current_playlist = []
        self._current_queue = []
        self._current_index = 0

        #0: Off, 1: artist, 2: album, 3: All
        self._shuffle_mode = 0
        self._repeat_mode = 0

        self._music_observer = MusicObserver(self)
        self._music_observer.start()

    def play_next(self):
        if self._current_index < len(self._current_playlist) - 1:
            self._current_index += 1
            self._current_music = None
            self.play()

    def play_prev(self):
        if self._current_index > 0:
            self._current_index -= 1
            self._current_music = None
            self.play()

    def current_title(self):
        return 'not_playing' if not self._current_music else self._current_music['title']

    def current_artist(self):
        return 'not_playing' if not self._current_music else self._current_music['album_artist']

    def current_album(self):
        return 'not_playing' if not self._current_music else self._current_music['album_title']

    def current_length(self):
        return 'not_playing' if not self._current_music else self._current_music['track_length']

    def play(self):
        if self._current_music is None:
            if not self._current_playlist:
                self.stop()
                return
            else:
                self._current_music = self._current_playlist[self._current_index]

        self.load(self._current_music['file_path'])
        pygame.mixer.music.play()

    def load(self, file_path):
        pygame.mixer.music.load(file_path)

    def play_from_id(self, music_id):
        self._current_music = self._finder.get_metadata(music_id)
        self.play()

    def queue(self, music_id):
        pass

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

    def set_list(self, list):
        self._current_playlist = list


class MusicObserver(Thread):
    TRACK_END = pygame.constants.USEREVENT + 1

    def __init__(self, player):
        Thread.__init__(self)
        self._player = player
        pygame.mixer.music.set_endevent(self.__class__.TRACK_END)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == self.__class__.TRACK_END:
                    self._player.play_next()
            time.sleep(0.1)
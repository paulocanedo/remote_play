import os
import time
import pygst
pygst.require("0.10")
import gst


from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from threading import Thread
from database import Database
from gst.extend.discoverer import Discoverer


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
                      mdata.info.length * 1000,
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
    def list_files_from_filesystem(base_dir, extensions={".mp3", ".m4a"}):
        file_list = []

        for root, subFolders, files in os.walk(base_dir):
            for f in files:
                for extension in extensions:
                    if f.endswith(extension):
                        path = os.path.join(root, f)
                        file_list.append(path)
        return file_list


class MusicPlayer:
    _gst_player = None

    def __init__(self, finder):
        self._finder = finder
        self._current_music = None
        self._current_playlist = []
        self._current_queue = []
        self._current_index = 0

        #0: Off, 1: artist, 2: album, 3: All
        self._shuffle_mode = 0
        self._repeat_mode = 0


        if self.__class__._gst_player is None:
            self.__class__._gst_player = GstPlayer()
            def on_eos():
                print "terminou a musica"

            self.__class__._gst_player.on_eos = lambda *x: on_eos()

        self._music_observer = MusicObserver(self.__class__._gst_player)
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

        self.stop()
        self.load(self._current_music['file_path'])
        self.__class__._gst_player.play()

    def load(self, file_path):
        self.__class__._gst_player.set_location('file://%s' % file_path)

    def play_from_id(self, music_id):
        self._current_music = self._finder.get_metadata(music_id)
        self.play()

    def queue(self, music_id):
        pass

    def pause(self):
        self.__class__._gst_player.pause()

    def resume(self):
        self.__class__._gst_player.play()

    def stop(self):
        self.__class__._gst_player.stop()

    def get_volume(self):
        return self.__class__._gst_player.get_volume()

    def set_volume(self, volume):
        self.__class__._gst_player.set_volume(volume)

    def get_position(self):
        pass

    def set_position(self, position):
        pass

    def set_list(self, list):
        self._current_playlist = list


class MusicObserver(Thread):
    def __init__(self, player):
        Thread.__init__(self)
        self._player = player

    def run(self):
        while True:
            position, duration = self._player.query_position()
            if position >= duration:
                print "acabou"
            time.sleep(0.3)
        pass


class GstPlayer:
    def __init__(self):
        self.playing = False
        self.player = gst.element_factory_make("playbin", "player")
        self.on_eos = False

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    def on_message(self, bus, message):
        print "message %s" % message
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.playing = False
            print "\n Unable to play audio. Error: ", \
            message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.playing = False

    def set_location(self, location):
        self.player.set_property('uri', location)

    def query_position(self):
        "Returns a (position, duration) tuple"
        try:
            position, format = self.player.query_position(gst.FORMAT_TIME)
        except:
            position = gst.CLOCK_TIME_NONE

        try:
            duration, format = self.player.query_duration(gst.FORMAT_TIME)
        except:
            duration = gst.CLOCK_TIME_NONE

        return (position, duration)

    def seek(self, location):
        """
        @param location: time to seek to, in nanoseconds
        """
        gst.debug("seeking to %r" % location)
        event = gst.event_new_seek(1.0, gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            gst.SEEK_TYPE_SET, location,
            gst.SEEK_TYPE_NONE, 0)

        res = self.player.send_event(event)
        if res:
            gst.info("setting new stream time to 0")
            self.player.set_new_stream_time(0L)
        else:
            gst.error("seek to %r failed" % location)

    def pause(self):
        gst.info("pausing player")
        self.player.set_state(gst.STATE_PAUSED)
        self.playing = False

    def play(self):
        gst.info("playing player")
        self.player.set_state(gst.STATE_PLAYING)
        self.playing = True

    def stop(self):
        self.player.set_state(gst.STATE_NULL)
        gst.info("stopped player")

    def get_state(self, timeout=1):
        return self.player.get_state(timeout=timeout)

    def is_playing(self):
        return self.playing

    def get_volume(self):
        return self.player.props.volume


    def set_volume(self, volume):
        self.player.props.volume = volume
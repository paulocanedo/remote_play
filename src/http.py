from BaseHTTPServer import BaseHTTPRequestHandler
import cStringIO
import json
import traceback
import config

from src.music import MusicFinder, MusicPlayer

TEXT_HTML = 'text/html'
APPLICATION_JSON = 'application/json'
APPLICATION_JAVA_SCRIPT = 'application/javascript'


class RemotePlayHttpHandler(BaseHTTPRequestHandler):
    _finder = None
    _music_player = None

    def __init__(self, request, client_address, server):
        if self.__class__._finder is None:
            self.__class__._finder = MusicFinder(config.MUSIC_DIRECTORY)
        if self.__class__._music_player is None:
            self.__class__._music_player = MusicPlayer(self.__class__._finder)
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def send_text_response(self, type, output):
        self.send_response(200)
        self.send_header('Content-type', "%s; charset=utf-8" % type)
        self.end_headers()

        self.wfile.write(output.getvalue())

    def get_html_begins(self):
        result = "<html><head><title></title></head><body>"
        return result

    def get_html_ends(self):
        result = "</body></html>"
        return result

    def do_GET(self):
        try:
            output = cStringIO.StringIO()
            response_type = TEXT_HTML

            if self.path == '/':
                output.write(self.get_html_begins())
                output.write('<p>Remote Play Index</p>')
                output.write(self.get_html_ends())

            if self.path.startswith("/html/"):
                html_file = self.path.replace('/html/', '', 1)
                with open('html/%s.htm' % html_file) as handle:
                    content = handle.read()
                    output.write(content)

            if self.path == "/js":
                response_type = APPLICATION_JAVA_SCRIPT
                with open('./js/rp.js') as handle:
                    content = handle.read()
                    output.write(content)

            if self.path.startswith("/play/"):
                music_id = self.path.replace('/play/', '', 1)

                self.__class__._music_player.play_from_id(music_id)

            if self.path.startswith("/set_volume/"):
                volume = self.path.replace('/set_volume/', '', 1)
                self.__class__._music_player.set_volume(float(volume) / 100.0)

            if self.path == '/play':
                self.__class__._music_player.play()

            if self.path == '/stop':
                self.__class__._music_player.stop()

            if self.path == '/pause':
                self.__class__._music_player.pause()

            if self.path == '/resume':
                self.__class__._music_player.resume()

            if self.path == '/play_next':
                self.__class__._music_player.play_next()

            if self.path == '/play_prev':
                self.__class__._music_player.play_prev()

            if self.path == '/current':
                response_type = APPLICATION_JSON

                response = {
                    'volume': self.__class__._music_player.get_volume(),
                    'position': self.__class__._music_player.get_position(),
                    'title': self.__class__._music_player.current_title(),
                    'artist': self.__class__._music_player.current_artist(),
                    'album': self.__class__._music_player.current_album(),
                    'length': self.__class__._music_player.current_length()
                }
                output.write(json.dumps(response))

            if self.path == '/list':
                response_type = APPLICATION_JSON
                musics = self.__class__._finder.list_musics()
                self.__class__._music_player.set_list(musics)
                output.write(json.dumps(musics))

            self.send_text_response(response_type, output)

        except:
            traceback.print_exc()
            self.send_error(500, 'The server failed: %s' % self.path)
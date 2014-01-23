from BaseHTTPServer import BaseHTTPRequestHandler
import cStringIO
import json
import traceback

from src.music import MusicFinder, MusicPlayer

TEXT_HTML = 'text/html'
APPLICATION_JSON = 'application/json'


class RemotePlayHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self._finder = MusicFinder("/home/paulocanedo/Downloads/Music")
        self._music_player = MusicPlayer(self._finder)
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
                with open('./html/%s.htm' % html_file) as handle:
                    content = handle.read()
                    output.write(content)

            if self.path.startswith("/play/"):
                music_id = self.path.replace('/play/', '', 1)

                self._music_player.play(music_id)

            if self.path.startswith("/set_volume/"):
                volume = self.path.replace('/set_volume/', '', 1)
                pygame.mixer.music.set_volume(float(volume) / 100.0)

            # if self.path == '/play':
            #     pygame.mixer.music.play()

            if self.path == '/stop':
                self._music_player.stop()

            if self.path == '/pause':
                self._music_player.pause()

            if self.path == '/resume':
                self._music_player.resume()

            if self.path == '/current':
                response_type = APPLICATION_JSON

                response = {
                    # 'volume': pygame.mixer.music.get_volume(),
                    # 'position': pygame.mixer.music.get_pos(),
                    'title': self._music_player.current_title()
                }
                output.write(json.dumps(response))

            if self.path == '/list':
                response_type = APPLICATION_JSON
                musics = self._finder.list_musics()
                output.write(json.dumps(musics))

            self.send_text_response(response_type, output)

        except:
            traceback.print_exc()
            self.send_error(500, 'The server failed: %s' % self.path)
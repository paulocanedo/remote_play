from BaseHTTPServer import BaseHTTPRequestHandler
import cStringIO
import pygame
import json

from src.music import MusicFinder

TEXT_HTML = 'text/html'
APPLICATION_JSON = 'application/json'


class RemotePlayHttpHandler(BaseHTTPRequestHandler):
    allow_reuse_address = True
    finder = MusicFinder("/home/paulocanedo/Music")

    def __init__(self, request, client_address, server):
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
                file_path = self.finder.get_file_path(music_id)
                output.write(file_path)
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()

            if self.path == '/play':
                pygame.mixer.music.play()

            if self.path == '/stop':
                pygame.mixer.music.stop()

            if self.path == '/pause':
                pygame.mixer.music.pause()

            if self.path == '/resume':
                pygame.mixer.music.unpause()

            if self.path == '/current':
                output.write(', %s' % pygame.mixer.music.get_pos())

            if self.path == '/list':
                response_type = APPLICATION_JSON
                musics = self.finder.list_musics()
                output.write(json.dumps(musics))

            self.send_text_response(response_type, output)

        except Exception:
            self.send_error(500, 'The server failed: %s' % self.path)
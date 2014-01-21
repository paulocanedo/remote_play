from BaseHTTPServer import BaseHTTPRequestHandler
import cStringIO
import pygame

from music import MusicFinder

TEXT_HTML = 'text/html'
APPLICATION_JSON = 'application_json'


class RemotePlayHttpHandler(BaseHTTPRequestHandler):
    allow_reuse_address = True
    finder = MusicFinder()

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
        output = cStringIO.StringIO()
        response_type = TEXT_HTML

        if self.path == '/':
            output.write(self.get_html_begins())
            output.write('<p>Remote Play Index</p>')
            output.write(self.get_html_ends())

        if self.path == '/play':
            pygame.mixer.music.load('music.mp3')
            pygame.mixer.music.play()

        if self.path == '/stop':
            pygame.mixer.music.stop()

        if self.path == '/pause':
            pygame.mixer.music.pause()

        if self.path == '/resume':
            pygame.mixer.music.unpause()

        if self.path == '/info':
            output.write(', %s' % pygame.mixer.music.get_pos())

        if self.path == '/list':
            response_type = APPLICATION_JSON
            output.write('["')
            output.write('","'.join(self.finder.list_files()))

            # for file in self.finder.list_files():
            #     if file.endswith(".m4a"):
            #         continue
            #
            #     f = tagpy.FileRef(file)
            #     output.write(f.tag().artist)
            #     output.write(',')

            output.write('"]')

        self.send_text_response(response_type, output)



        # return
        #
        # except IOError:
        # self.send_error(404,'File Not Found: %s' % self.path)
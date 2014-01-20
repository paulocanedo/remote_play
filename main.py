import os
import pygame
import cStringIO
import logging

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer

__author__ = 'paulocanedo'

class MusicFinder:

    def __init__(self):
        self.music = "/home/paulocanedo/Music"
        self.fileList = []

    def list_files(self):
        del self.fileList[:]

        extensions = {".mp3", ".m4a", ".flac"}

        for root, subFolders, files in os.walk(self.music):
            for file in files:
                for extension in extensions:
                    if(file.endswith(extension)):
                        self.fileList.append(os.path.join(root,file))
        return self.fileList

class MyHandler(BaseHTTPRequestHandler):
    allow_reuse_address = True
    finder = MusicFinder()

    def __init__(self, request, client_address, server):
		BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    # I WANT TO EXTRACT imsi parameter here and send a success response to
    # back to the client.
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers()

        output = cStringIO.StringIO()
        output.write("<html><head>")
        output.write("<style type=\"text/css\">")
        output.write("h1 {color:blue;}")
        output.write("h2 {color:red;}")
        output.write("</style>")
        output.write("Paulo Canedo")

        if self.path == '/play':
            # if pygame.mixer.music.get_busy() == False:
            # pygame.mixer.music.load('/home/paulocanedo/Music/iTunes/iTunes Media/Music/Engenheiros do Hawaii/10.000 Destinos - Ao Vivo/01 A Montanha.m4a')
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
            output.write('list: <BR >')
            for file in MusicFinder().list_files():
                output.write('%s<br />' % file)

        output.write("</body>")
        output.write("</html>")

        self.wfile.write(output.getvalue())

        # return
        #
        # except IOError:
        # self.send_error(404,'File Not Found: %s' % self.path)

PORT = 8000

# Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

pygame.init()
pygame.mixer.init()

print "serving at port", PORT
httpd.serve_forever()
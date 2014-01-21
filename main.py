import SocketServer
import pygame

from http import RemotePlayHttpHandler

__author__ = 'paulocanedo'

PORT = 8000

handler = RemotePlayHttpHandler
httpd = SocketServer.TCPServer(("", PORT), handler)

pygame.init()
pygame.mixer.init()

print "serving at port", PORT
httpd.serve_forever()
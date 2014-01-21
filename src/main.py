import SocketServer
import pygame

from src.http import RemotePlayHttpHandler

PORT = 8000

handler = RemotePlayHttpHandler
httpd = SocketServer.TCPServer(("", PORT), handler)

pygame.init()
pygame.mixer.init()

print "serving at port", PORT
httpd.serve_forever()
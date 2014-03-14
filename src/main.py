import SocketServer

from src.http import RemotePlayHttpHandler

PORT = 8000

handler = RemotePlayHttpHandler
httpd = SocketServer.TCPServer(("", PORT), handler)

print "serving at port", PORT
httpd.serve_forever()
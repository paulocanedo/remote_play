import sys, string,cStringIO, cgi,time,datetime
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

class MyHandler(BaseHTTPRequestHandler):

	# I WANT TO EXTRACT imsi parameter here and send a success response to 
	# back to the client.
	def do_GET(self):
	    try:
	        if self.path.endswith(".html"):
	            #self.path has /index.htm
	            f = open(curdir + sep + self.path)
	            self.send_response(200)
	            self.send_header('Content-type','text/html')
	            self.end_headers()
	            self.wfile.write("<h1>Device Static Content</h1>")
	            self.wfile.write(f.read())
	            f.close()
	            return
	        if self.path.endswith(".esp"):   #our dynamic content
	            self.send_response(200)
	            self.send_header('Content-type','text/html')
	            self.end_headers()
	            self.wfile.write("<h1>Dynamic Dynamic Content</h1>")
	            self.wfile.write("Today is the " + str(time.localtime()[7]))
	            self.wfile.write(" day in the year " + str(time.localtime()[0]))
	            return

	        # The root
	        self.send_response(200)
	        self.send_header('Content-type','text/html')
	        self.end_headers()

	        output = cStringIO.StringIO()
	        output.write("<html><head>")
	        output.write("<style type=\"text/css\">")
	        output.write("h1 {color:blue;}")
	        output.write("h2 {color:red;}")
	        output.write("</style>")
	        output.write("Paulo Canedo")
	        # output.write("<h1>Device #" + n + " Root Content</h1>")
	        # output.write("<h2>Device Time: " + now.strftime("%Y-%m-%d %H:%M:%S") + "</h2>")
	        output.write("</body>")
	        output.write("</html>")

	        self.wfile.write(output.getvalue())

	        return

	    except IOError:
	        self.send_error(404,'File Not Found: %s' % self.path)

PORT = 8000

# Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
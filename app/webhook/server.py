try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from .executor import WebhookExecutor

class WebhookHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path.startswith('/webhook/'):
            token = self.path.replace('/webhook/', '')
            if WebhookExecutor().deploy(token):
                self.send_response(200)
            else:
                self.send_response(401, "Unauthorized")
        else:
            self.send_response(404)
        self.end_headers()


def run(host='', port=7000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, WebhookHTTPRequestHandler)
    print(" * Running on port %d (Press CTRL+C to quit)" % port)
    httpd.serve_forever()

# A tiny web app that greets you by name.
import http.server
import os

name = os.environ["APP_NAME"]


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"Hello from {name}!\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


print("broken-app listening on port 8000", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()

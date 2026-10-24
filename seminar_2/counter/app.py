# Counts visits and how many times it has started. Both numbers live in /data,
# so they survive the container being replaced, if /data is a volume.
import http.server
import json
import os

DATA = "/data"
os.makedirs(DATA, exist_ok=True)


def read(name):
    path = os.path.join(DATA, name)
    return int(open(path).read()) if os.path.exists(path) else 0


def bump(name):
    n = read(name) + 1
    with open(os.path.join(DATA, name), "w") as f:
        f.write(str(n))
    return n


starts = bump("starts")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/crash":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Crashing now.\n")
            self.wfile.flush()
            os._exit(1)
        if self.path == "/stats":
            body = json.dumps({"visits": read("visits"), "starts": starts}) + "\n"
        else:
            visits = bump("visits")
            body = f"Hello! Visit number {visits}. This app has started {starts} time(s).\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):
        pass


print(f"counter listening on port 8000, start number {starts}", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()

"""Read-only fictional advisory. Only this fixed HTML document is ever served."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ADVISORY = (Path(__file__).resolve().parent / 'vendor-portal' / 'index.html').read_bytes()


class AdvisoryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond(send_body=True)

    def do_HEAD(self):
        self.respond(send_body=False)

    def respond(self, *, send_body):
        if urlsplit(self.path).path not in ('/', '/advisories/case-1042'):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(ADVISORY)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        if send_body:
            self.wfile.write(ADVISORY)


if __name__ == '__main__':
    with ThreadingHTTPServer(('127.0.0.1', 8787), AdvisoryHandler) as server:
        print('Synthetic advisory only: http://127.0.0.1:8787/advisories/case-1042', flush=True)
        server.serve_forever()

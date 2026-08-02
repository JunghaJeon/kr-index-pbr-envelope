"""검증용 정적 서버. SimpleHTTPRequestHandler 는 charset 을 안 붙여 한글이 깨진다."""

import http.server
import socketserver


class H(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        t = super().guess_type(path)
        return t + "; charset=utf-8" if t == "text/html" else t

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
print("serving on 8732", flush=True)
socketserver.TCPServer(("127.0.0.1", 8732), H).serve_forever()

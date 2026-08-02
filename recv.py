"""브라우저(https://data.krx.co.kr)가 수집한 데이터를 로컬 파일로 받는 임시 수신 서버.

https 페이지 -> http://localhost 요청은 Chrome의 Private Network Access 대상이라
preflight 에 Access-Control-Allow-Private-Network 를 돌려줘야 통과한다.
"""

import http.server
import socketserver
from pathlib import Path

BASE = Path(__file__).resolve().parent
PORT = 8891


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type, x-name")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "600")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        name = self.headers.get("x-name", "data")
        name = "".join(c for c in name if c.isalnum() or c in "._-") or "data"
        n = int(self.headers.get("content-length", 0))
        body = self.rfile.read(n)
        (BASE / name).write_bytes(body)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"saved {name} {len(body)}".encode())

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
print(f"listening on {PORT}", flush=True)
socketserver.TCPServer(("127.0.0.1", PORT), Handler).serve_forever()

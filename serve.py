"""정적 서버.

- SimpleHTTPRequestHandler 는 charset 을 안 붙여 한글이 깨진다.
- 단일 스레드 서버는 keep-alive 연결 하나에 막혀 다음 요청을 못 받는다.
  브라우저와 터널이 동시에 붙으므로 ThreadingHTTPServer 를 쓴다.
"""

import http.server
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8732


class H(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        t = super().guess_type(path)
        return t + "; charset=utf-8" if t == "text/html" else t

    def log_message(self, *a):
        pass


class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


print(f"serving on 127.0.0.1:{PORT}", flush=True)
Server(("127.0.0.1", PORT), H).serve_forever()

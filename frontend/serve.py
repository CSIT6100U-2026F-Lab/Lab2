"""
Serve the static Code Explorer UI.

From the project root:
    python3 frontend/serve.py

Listens on 127.0.0.1:5500. REST and GraphQL are separate processes.
"""

import http.server
import os
import sys

HOST = "127.0.0.1"
PORT = 5500

_FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))


class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=_FRONTEND_DIR, **kwargs)


def main():
    server = http.server.ThreadingHTTPServer((HOST, PORT), FrontendHandler)
    print("Frontend:  http://{}:{}/".format(HOST, PORT), flush=True)
    print("Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

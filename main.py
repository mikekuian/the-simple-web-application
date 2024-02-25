import socketserver
import threading
import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket
from datetime import datetime
import urllib.parse


# HTTP Server Handler
class WebServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path in ["/", "/index.html"]:
            self.path = "/index.html"
        elif self.path == "/message.html":
            self.path = "/message.html"
        elif self.path in ["/style.css", "/logo.png"]:
            pass  # SimpleHTTPRequestHandler
        else:
            self.path = "/error.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            self.send_data_to_udp_server(post_data)
            self.send_response(302)
            self.send_header("Location", "/message.html")
            self.end_headers()

    def send_data_to_udp_server(self, data):

        # UDP server

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, ("localhost", 5000))
        sock.close()


# UDP Server Handler
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        data_dict = urllib.parse.parse_qs(data.decode("utf-8"))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.save_data(timestamp, {k: v[0] for k, v in data_dict.items()})

    def save_data(self, timestamp, data):
        # save data in JSON file

        path = "storage/data.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, "r+") as file:
                content = json.load(file)
                content[timestamp] = data
                file.seek(0)
                file.truncate()
                json.dump(content, file, indent=2)
        else:
            with open(path, "w") as file:
                json.dump({timestamp: data}, file, indent=2)


# run of HTTP server
def run_web_server():
    port = 3000
    httpd = HTTPServer(("", port), WebServerHandler)
    print(f"HTTP Server running on port {port}")
    httpd.serve_forever()


# run of UDP server
def run_udp_server():
    port = 5000
    server = socketserver.UDPServer(("localhost", port), UDPHandler)
    print(f"UDP Server running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    threading.Thread(target=run_udp_server).start()

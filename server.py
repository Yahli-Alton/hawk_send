from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps


class MessangerServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        path_split = self.path.split('/')[1::]

    def create_channel(self, path_split):
        return NotImplemented

    def create_user(self, path_split):
        return NotImplemented

    def upload_message(self, path_split):
        return NotImplemented

    def download_channel(self, path_split):
        return NotImplemented

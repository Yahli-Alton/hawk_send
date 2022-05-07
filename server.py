import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from DataBaseFile import *
import time


class MessangerServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = json.loads(self.rfile.read(content_length).decode())
        print(f"data: {post_data}")

        functions = {"validate_user": self.validate_user,
                     "create_channel": self.create_channel,
                     "create_user": self.create_user,
                     "upload_message": self.upload_message,
                     "download_channel": self.download_channel}

        self._set_response()
        self.request = self.path.split('/')[1::]
        print(self.request)

        if self.request[0] == "create_user":
            self.create_user(post_data)
        elif self.request[0] in functions.keys():
            if self.validate_user(post_data):
                print("calling action")
                functions[self.request[0]](post_data)

    def validate_user(self, data):
        # /username-password
        self.username = data["username"]
        self.password = data["password"]

        print(f"username {self.username}, password {self.password}, database password {database.get_password(self.username)}")
        if self.password != database.get_password(self.username):
            return False

        self.wfile.write(bytes("passed validation\n", "utf-8"))
        print("passed validation")
        return True

    def create_channel(self, data):
        print("in create_channel")
        channel_id = database.create_channel(channel_name=data["channel_name"],
                                             usernames=data["users"])

        self.wfile.write(bytes(str(channel_id), "utf-8"))
        return True

    def create_user(self, data):
        username, password = data["username"], data["password"]
        database.create_user(username=username,
                             password=password)

        self.wfile.write(bytes(f"created user {username}", "utf-8"))
        print(username)
        return True

    def upload_message(self, data):
        text, channel_id, _time = data["message"], data["channel_id"], time.time()
        username = data["username"]

        if database.verify_user_access(channel_id=channel_id, username=username):
            database.upload_message(channel_id=channel_id,
                                    message=Message(_time=_time,
                                                    username=self.username,
                                                    text=text))
            self.wfile.write(bytes(f"send {text}", "utf-8"))
            print(text)
            return
        else:
            self.wfile.write(bytes("You don't have access", "utf-8"))

    def download_channel(self, data: dict):
        channel_id = data["channel_id"]
        if database.verify_user_access(channel_id=channel_id, username=data["username"]):
            channel: dict = database.download_channel(channel_id=channel_id)

            self.wfile.write(bytes(json.dumps(channel), "utf-8"))
            print(channel)
            return True
        else:
            self.wfile.write(bytes("You don't have access", "utf-8"))


hostName, serverPort = "0.0.0.0", 5690

USERS_PATH = "/Users/talkaridi/Desktop/WhatUp/caching/users.json"
CHANNELS_PATH = "/Users/talkaridi/Desktop/WhatUp/caching/channels.json"
ID_PATH = "/Users/talkaridi/Desktop/WhatUp/caching/id.txt"

database = DataBase.from_cache(USERS_PATH, CHANNELS_PATH, ID_PATH)
print(database.channels)
print(database.users)


webServer = HTTPServer((hostName, serverPort), MessangerServer)
print("Server started http://%s:%s" % (hostName, serverPort))
print(f"public ip: {socket.gethostbyname(socket.gethostname())}")

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")

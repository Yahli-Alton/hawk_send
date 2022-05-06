import json
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
        # /username-password/create_channel/channel_name/username-username....
        print("in create_channel")
        database.create_channel(channel_name=data["channel_name"],
                                users=data["users"].split("-"))

        self.wfile.write(bytes(f"created_channel", "utf-8"))
        return True

    def create_user(self, data):
        # create_user/username-password
        username, password = data["username"], data["password"]
        database.create_user(username=username,
                             password=password)

        self.wfile.write(bytes(f"created user {username}", "utf-8"))
        print(username)
        return True

    def upload_message(self, data):
        # username-password/upload_message/channel/message
        channel, text, _time = data["channel"], data["message"], time.time()
        database.upload_message(channel_name=channel,
                                message=Message(_time=_time,
                                                username=self.username,
                                                text=text))
        self.wfile.write(bytes(f"send {text}", "utf-8"))
        print(text)
        return True

    def download_channel(self, data: dict):
        # username-password/download_channel/channel_name
        channel_name = data["channel_name"]
        channel: dict = database.download_channel(channel_name=channel_name)

        self.wfile.write(bytes(json.dumps(channel), "utf-8"))
        print(channel)
        return True


hostName, serverPort = "localhost", 8080

database = DataBase()


webServer = HTTPServer((hostName, serverPort), MessangerServer)
print("Server started http://%s:%s" % (hostName, serverPort))

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")

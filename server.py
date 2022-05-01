import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from DataBaseFile import DataBase


class MessangerServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.request = self.path.split('/')[1::]

        if self.request != ['favicon.ico']:
            if self.request[1] != "create_user":
                if not self.validate_user(self.request):
                    print("now validated")
                    return False

            functions = {"validate_user": self.validate_user,
                         "create_channel": self.create_channel,
                         "create_user": self.create_user,
                         "upload_message": self.upload_message,
                         "download_channel": self.download_channel}

            print("calling action")
            functions[self.request[1]](self.request)

    def validate_user(self, request):
        # /username-password
        self.username, self.password = request[0].split("-")
        print(f"username {self.username}, password {self.password}, database password {database.get_password(self.username)}")
        if self.password != database.get_password(self.username):
            return False

        self.wfile.write(bytes("passed validation\n", "utf-8"))
        print("passed validation")
        return True

    def create_channel(self, request):
        # /username-password/create_channel/channel_name/username-username....
        print("in create_channel")
        database.create_channel(channel_name=request[2],
                                users=request[3].split("-"))

        self.wfile.write(bytes(f"created_channel {request[2]}\n", "utf-8"))
        print(request[2])
        return True

    def create_user(self, request):
        # create_user/username-password
        username, password = request[0].split("-")
        database.create_user(username=username,
                             password=password)

        self.wfile.write(bytes(f"created user {username}\n", "utf-8"))
        print(username)
        return True

    def upload_message(self, request):
        # username-password/upload_message/channel/message
        channel, text, _time = request[2], request[3], time.time()
        database.upload_message(channel_name=channel,
                                message=Message(_time=_time,
                                                username=self.username,
                                                text=text))
        self.wfile.write(bytes(f"send {text}\n", "utf-8"))
        print(text)
        return True

    def download_channel(self, request: str):
        # username-password/download_channel/channel_name
        channel_name = request[2]
        channel: dict = database.download_channel(channel_name=channel_name)

        self.wfile.write(bytes(json.dumps(channel) + "\n", "utf-8"))
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
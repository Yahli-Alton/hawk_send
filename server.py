from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps
from DataBase import DataBase, Message
import time
from typing import List

database = DataBase()


class MessangerServer(BaseHTTPRequestHandler):
    def __init__(self):
        BaseHTTPRequestHandler.__init__(self, self.request, self.client_address, self.server)
        self.username, self.password = "", ""
        self.request: List[str] = []

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.request = self.path.split('/')[1::]
        if self.request[0] != "create_user":
            if not self.validate_user(self.request):
                return False

        functions = {"validate_user": self.validate_user,
                     "create_channel": self.create_channel,
                     "create_user": self.create_user,
                     "upload_message": self.upload_message,
                     "download_channel": self.create_channel}

        functions[self.request[0]]()

    def validate_user(self, request):
        # /username-password
        self.username, self.password = request[0].split("-")
        if self.password != database.get_password(self.username):
            return False
        return True

    def create_channel(self, request):
        # /username-password/create_channel/channel_name/username-username....
        database.create_channel(channel_name=request[2],
                                users=request[3].split("-"))
        return True

    def create_user(self, request):
        # create_user/username-password
        username, password = request[1].split("-")
        database.create_user(username=username,
                             password=password)
        return True

    def upload_message(self, request):
        # username-password/upload_message/channel/message
        channel, text, time = request[2], request[3], time.time()
        database.upload_message(channel_name=channel,
                                message=Message(time=time,
                                                username=self.username,
                                                text=text))

    def download_channel(self, request: str):
        # username-password/download_channel/channel_name
        channel_name = request[2]
        channel: dict = database.download_channel(channel_name=channel_name)

        return channel

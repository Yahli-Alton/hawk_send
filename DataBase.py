import json
from typing import List


class Message:
    def __int__(self, time, username, message):
        self.time = time
        self.username = username
        self.message = message


class Channel:
    def __init__(self, users, channel_name):
        self.users: List[User] = users
        self.channel_name: str = channel_name
        self.message: List[Message] = []

    def upload_message(self, message):
        return NotImplemented

    def download_channel(self):
        return NotImplemented

    def sort_channel(self):
        return NotImplemented


class User:
    def __init__(self, username, password, channels):
        self.username = username
        self.password = password
        self.channels: List[Channel] = channels


class DataBase:
    def __init(self):
        # {user: User}
        self.users: dict = {}
        # {"channel_name": channel}
        self.channels: dict = []

    def create_user(self, username, password):
        return NotImplemented
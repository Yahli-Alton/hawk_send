import time
from typing import List


class Message:
    def __int__(self, time, username, text):
        self.time = time
        self.username = username
        self.text = text


class Channel:
    def __init__(self, users, channel_name):
        self.users: List[User] = users
        self.channel_name: str = channel_name
        self.messages: List[Message] = []

    def upload_message(self, message):
        self.messages.append(message)

    def download_channel(self):
        self.sort_channel()
        final_messages = []
        for message in self.messages:
            _time = time.localtime(message.time)
            time_str = f"data: {_time.tm_year, _time.tm_mon, _time.tm_day}\nhour: {_time.tm_hour}\nminute: {_time.tm_min}"
            final_messages.append({"time": time_str,
                                   "username": message.username,
                                   "text": message.text})
        return final_messages

    def sort_channel(self):
        self.messages.sort(key=lambda x: x._time)
        return True


class User:
    def __init__(self, username, password, channels):
        self.username = username
        self.password = password
        self.channels: List[Channel] = channels


class DataBase:
    def __init(self):
        # {username: User}
        self.users: dict = {}
        # {"channel_name": channel}
        self.channels: dict = []

    def create_user(self, username, password):
        if username not in self.users.keys():
            self.users[username] = User(username, password, [])
            return True
        return "username already found"

    def create_channel(self, channel_name, users):
        if channel_name not in self.channels.keys():
            self.channels[channel_name] = Channel(channel_name=channel_name,
                                                  users=users)
        return "channel name already found"

    def upload_message(self, channel_name, message: Message):
        self.channels[channel_name].upload_message(message=message)
        return True

    def download_channel(self, channel_name: str):
        return self.channels[channel_name].download_channel()


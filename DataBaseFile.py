import time
from typing import List
import json


class ID_Maneger:
    def __init__(self, _id=0):
        self.id = _id

    def get_id(self):
        self.id += 1
        return self.id

    def cache(self):
        return self.id

    @staticmethod
    def from_cache(_id):
        return ID_Maneger(_id)


class Message:
    def __init__(self, _time, username, text):
        self._time = _time
        self.username = username
        self.text = text

    def cache(self) -> dict:
        return {"time": self._time,
                "username": self.username,
                "text": self.text}

    @staticmethod
    def from_cache(cache: dict):
        return Message(cache["time"], cache["username"], cache["text"])


class Channel:
    def __init__(self, usernames, channel_name, channel_id: int):
        self.usernames: List[str] = usernames
        self.channel_name: str = channel_name
        self.messages: List[Message] = []
        self.id = channel_id

    def upload_message(self, message):
        self.messages.append(message)

    def download_channel(self):
        self.sort_channel()
        final_messages = []
        for message in self.messages:
            _time = time.localtime(message._time)
            time_str = f"data: {_time.tm_year, _time.tm_mon, _time.tm_mday}\nhour: {_time.tm_hour}\nminute: {_time.tm_min}"
            final_messages.append({"time": time_str,
                                   "username": message.username,
                                   "text": message.text})
        return final_messages

    def sort_channel(self):
        self.messages.sort(key=lambda x: x._time)
        return True

    def cache(self):
        return {"usernames": self.usernames,
                "channel_name": self.channel_name,
                "messages": [message.cache() for message in self.messages],
                "id": self.id}

    @staticmethod
    def from_cache(cache: dict):
        usernames = cache["usernames"]
        channel_name = cache["channel_name"]
        messages = [Message.from_cache(message_cache) for message_cache in cache["messages"]]

        channel = Channel(usernames=usernames, channel_name=channel_name, channel_id=cache["id"])
        channel.messages = messages

        return channel


class User:
    def __init__(self, username, password, channels_ids: List[int]):
        self.username = username
        self.password = password
        self.channels_ids = channels_ids

    def cache(self):
        return {"username": self.username,
                "password": self.password,
                "channel_ids": self.channels_ids}

    @staticmethod
    def from_cache(cache: dict):
        return User(cache["username"], cache["password"], cache["channel_ids"])


class DataBase:
    def __init__(self, users_path, channels_path, id_path, last_id=0):
        # {username: User}
        self.users: dict = {}
        # {"channel_id": channel}
        self.channels: dict = {}
        self.id_manager = ID_Maneger(last_id)

        self.users_path = users_path
        self.channels_path = channels_path
        self.id_path = id_path

    def verify_user_access(self, channel_id, username):
        return username in self.channels[channel_id].usernames

    def create_user(self, username, password):
        print(self.users)
        if username not in self.users.keys():
            user = User(username, password, [])
            self.users[username] = user

            users_cache = json.load(open(self.users_path, "r"))
            users_cache[username] = user.cache()
            json.dump(users_cache, open(self.users_path, "w"))
            return True

        return "username already found"

    def create_channel(self, channel_name, usernames):
        channel_id = self.id_manager.get_id()
        channel = Channel(channel_name=channel_name,
                          usernames=usernames,
                          channel_id=channel_id)

        self.channels[str(channel_id)] = channel
        for username in usernames:
            self.users[username].channels_ids.append(channel_id)

        channels = json.load(open(self.channels_path, "r"))
        channels[channel_id] = channel.cache()
        json.dump(channels, open(self.channels_path, "w"))

        with open(self.id_path, "w") as file:
            file.write(str(channel_id))

        return channel_id

    def upload_message(self, channel_id, message: Message):
        self.channels[channel_id].upload_message(message=message)
        channels = json.load(open(self.channels_path, "r"))
        channels[str(channel_id)]["messages"].append(message.cache())
        json.dump(channels, open(self.channels_path, "w"))
        return True

    def download_channel(self, channel_id: str):
        return self.channels[channel_id].download_channel()

    def get_password(self, username):
        return self.users[username].password

    @staticmethod
    def from_cache(users_path, channels_path, id_path):
        users_database = json.load(open(users_path, "r"))

        users = {}
        for username in users_database.keys():
            users[username] = User.from_cache(users_database[username])

        channels_database = json.load(open(channels_path, "r"))

        channels = {}
        for channel_id in channels_database.keys():
            channels[channel_id] = Channel.from_cache(channels_database[channel_id])

        with open(id_path, "r") as file:
            last_id = int(file.read())

        database = DataBase(users_path=users_path,
                            channels_path=channels_path,
                            id_path=id_path,
                            last_id=last_id)
        database.users = users
        database.channels = channels

        return database

import time
from typing import List, Dict
import json
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


class Serializable(ABC):
    @abstractmethod
    def serialize(self) -> dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, serialized):
        raise NotImplementedError


class TriviallySerializableDataclass(Serializable):
    def serialize(self) -> dict:
        return asdict(self)  # noqa

    @classmethod
    def deserialize(cls, serialized):
        return cls(**serialized)  # noqa


@dataclass
class IdManager(TriviallySerializableDataclass):
    nxt: int = 0

    def assign_id(self):
        assigned = self.nxt
        self.nxt += 1
        return assigned


@dataclass(frozen=True)
class Message(TriviallySerializableDataclass):
    creation_time: float
    username: str
    content: str


@dataclass
class Channel(Serializable):
    usernames: List[str]
    channel_name: str
    channel_id: int
    messages: List[Message] = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []

    def upload_message(self, message):
        self.messages.append(message)

    def download_channel(self):
        self.sort_channel()
        final_messages = []
        for message in self.messages:
            _time = time.localtime(message.creation_time)
            time_str = {"hour": _time.tm_hour,
                        "minute": _time.tm_min,
                        "second": _time.tm_sec,
                        "date": f"{_time.tm_mon}.{_time.tm_mday}.{_time.tm_year}"}
            final_messages.append({"time": time_str,
                                   "username": message.username,
                                   "text": message.content})
        return final_messages

    def sort_channel(self):
        self.messages.sort(key=lambda msg: msg.creation_time)
        return True

    def serialize(self):
        return {"usernames": self.usernames,
                "channel_name": self.channel_name,
                "messages": [asdict(message) for message in self.messages],
                "id": self.channel_id}

    @classmethod
    def deserialize(cls, dct: dict):
        usernames = dct["usernames"]
        channel_name = dct["channel_name"]
        messages = [Message(**cached_message) for cached_message in dct["messages"]]

        return Channel(usernames=usernames, channel_name=channel_name, channel_id=dct["id"], messages=messages)


@dataclass(frozen=True)
class User(TriviallySerializableDataclass):
    username: str
    password: str
    channel_ids: List[int]


class Database:
    def __init__(self, users_path, channels_path, id_path, next_id=0):
        # {username: User}
        self.users: Dict[str, User] = {}
        # {"channel_id": channel}
        self.channels: Dict[int, Channel] = {}
        self.id_manager = IdManager(next_id)

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

            self.flush(flush_users=True)
            return True

        return False

    def create_channel(self, channel_name, usernames):
        channel_id = self.id_manager.assign_id()
        channel = Channel(channel_name=channel_name,
                          usernames=usernames,
                          channel_id=channel_id)

        self.channels[channel_id] = channel
        for username in usernames:
            self.users[username].channel_ids.append(channel_id)

        self.flush(flush_channels=True, flush_channel_id=True, flush_users=True)
        return channel_id

    def upload_message(self, channel_id, message: Message):
        self.channels[channel_id].upload_message(message=message)
        self.flush(flush_channels=True)
        return True

    def download_channel(self, channel_id: int):
        return self.channels[channel_id].download_channel()

    def get_password(self, username):
        return self.users[username].password

    def flush(self, flush_users: bool = False, flush_channels: bool = False, flush_channel_id: bool = False):
        if flush_users:
            with open(self.users_path, 'w') as file:
                json.dump({k: v.serialize() for k, v in self.users.items()}, file)
        if flush_channels:
            with open(self.channels_path, 'w') as file:
                json.dump({k: v.serialize() for k, v in self.channels.items()}, file)
        if flush_channel_id:
            with open(self.id_path, "w") as file:
                file.write(str(self.id_manager.nxt))

    @staticmethod
    def load_database(users_path, channels_path, id_path):
        users_database = json.load(open(users_path, "r"))

        users = {}
        for username in users_database.keys():
            users[username] = User.deserialize(users_database[username])

        channels_database = json.load(open(channels_path, "r"))

        channels = {}
        for channel_id in channels_database.keys():
            channels[int(channel_id)] = Channel.deserialize(channels_database[channel_id])

        with open(id_path, "r") as file:
            next_id = int(file.read())

        database = Database(users_path=users_path,
                            channels_path=channels_path,
                            id_path=id_path,
                            next_id=next_id)
        database.users = users
        database.channels = channels

        return database

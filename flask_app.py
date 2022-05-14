from DataBaseFile import *
import time
from flask import Flask, request
import werkzeug.exceptions
from pathlib import Path


app = Flask(__name__)


hostname, port = "0.0.0.0", 5690

USERS_PATH = str((Path(__file__).parent / "caching" / "users.json").absolute())
CHANNELS_PATH = str((Path(__file__).parent / "caching" / "channels.json").absolute())
ID_PATH = str((Path(__file__).parent / "caching" / "id.txt").absolute())

database = Database.load_database(USERS_PATH, CHANNELS_PATH, ID_PATH)


class BadCredentials(werkzeug.exceptions.HTTPException):
    code = 507
    description = 'Bad credentials'

    def __init__(self, reason: str = None):
        if reason:
            self.description = BadCredentials.description + '\n' + reason


@app.errorhandler(BadCredentials)
def handle_bad_credentials(e):
    return 'Bad Credentials!', 401


def authenticate():
    if not request.authorization:
        print("No authorization")
        raise BadCredentials()

    username = request.authorization.username
    password = request.authorization.password
    if password != database.get_password(username):
        print(f"Incorrect login attempt for {username}")
        raise BadCredentials()

    return username


@app.route('/create_user', methods=['POST'])
def create_user():
    username, password = request.json["username"], request.json["password"]
    if database.create_user(username=username,
                            password=password):
        return f"Successfully created user {username}"
    else:
        return f"User {username} already exists :(", 401


@app.route('/create_channel', methods=['POST'])
def create_channel():
    authenticate()
    channel_id = database.create_channel(channel_name=request.json["channel_name"],
                                         usernames=request.json["users"])

    return str(channel_id)


@app.route('/upload_message', methods=['POST'])
def upload_message():
    username = authenticate()
    text, channel_id, _time = request.json["message"], int(request.json["channel_id"]), time.time()

    if database.verify_user_access(channel_id=channel_id, username=username):
        database.upload_message(channel_id=channel_id,
                                message=Message(creation_time=_time,
                                                username=username,
                                                content=text))
        return "Message sent successfully!"
    else:
        raise BadCredentials(f'Username not part of channel #{channel_id}')


@app.route('/download_channel', methods=['GET'])
def download_channel():
    username = authenticate()
    channel_id = int(request.args.get('channel_id'))
    if database.verify_user_access(channel_id=channel_id, username=username):
        channel = database.download_channel(channel_id=channel_id)
        return {'channel': channel}
    else:
        raise BadCredentials(f'Username not part of channel #{channel_id}')


@app.route("/get_user_channel_ids", methods=['GET'])
def get_user_channel_ids():
    username = authenticate()
    return {"channel_names": [database.channels[channel_id].channel_name for channel_id in database.users[username].channel_ids],
            "channel_ids": database.users[username].channel_ids}


if __name__ == '__main__':
    app.run(hostname, port)

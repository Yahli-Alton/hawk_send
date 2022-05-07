import requests
import json


session = requests.Session()
session.auth = ('tal-kh', '123')

URL = "http://nickjohnson.pythonanywhere.com/"


print(requests.post(url=URL + "create_user",
                    json={"username": "tal-kh", "password": "123"}).text)

resp = session.post(url=URL + "create_channel",
                    json={"channel_name": "tal", "users": ["tal-kh"]}).text
chan_id = int(resp.split("\n")[-1])

print(session.post(url=URL+"upload_message",
                   json={
                        "channel_id": str(2),
                        "message": "hello"
                    }).text)


channel = session.get(url=URL + "download_channel",
                      params={"channel_id": "2"}).json()['channel']

print(channel)

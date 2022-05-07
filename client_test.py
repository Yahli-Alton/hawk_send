import requests
import json

URL = "http://192.168.1.14:5690/"
print(requests.post(url=URL + "create_user",
                    data=json.dumps({"username": "tal-kh", "password": "123"})).text)

resp = requests.post(url=URL + "create_channel",
                    data=json.dumps({"username": "tal-kh",
                                     "password": "123",
                                     "channel_name": "tal",
                                     "users": ["tal-kh"]})).text
chan_id = int(resp.split("\n")[-1])

print(requests.post(url=URL+"upload_message",
                    data=json.dumps({
                        "username": "tal-kh",
                        "password": "123",
                        "channel_id": str(chan_id),
                        "message": "hello"
                    })).text)

channel = requests.post(url=URL + "download_channel",
                        data=json.dumps({
                            "username": "tal-kh",
                            "password": "123",
                            "channel_id": str(chan_id)
                    })).text.split("\n")[-1]

print(channel)
print(type(eval(channel)))

import requests
import json

URL = "http://localhost:8080/"
print(requests.post(url=URL + "create_user",
                    data=json.dumps({"username": "tal-kh", "password": "123"})).text)

print(requests.post(url=URL + "create_channel",
                    data=json.dumps({"username": "tal-kh",
                                     "password": "123",
                                     "channel_name": "tal",
                                     "users": "tal-kh"})).text)

print(requests.post(url=URL+"upload_message",
                    data=json.dumps({
                        "username": "tal-kh",
                        "password": "123",
                        "channel": "tal",
                        "message": "hello"
                    })).text)

channel = requests.post(url=URL + "download_channel",
                    data=json.dumps({
                        "username": "tal-kh",
                        "password": "123",
                        "channel_name": "tal"
                    })).text.split("\n")[-1]

print(eval(channel))
print(len(eval(channel)))
print("")

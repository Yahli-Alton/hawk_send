import requests


session = requests.Session()
session.auth = ('tal-kh', '123')

URL = "http://127.0.0.1:5690/"

"""
print(requests.post(url=URL + "create_user",
                    json={"username": "tal-kh", "password": "123"}).text)

resp = session.post(url=URL + "create_channel",
                    json={"channel_name": "tal", "users": ["tal-kh"]}).text
chan_id = int(resp.split("\n")[-1])
"""

for i in range(10):
    print(session.post(url=URL+"upload_message",
                       json={
                            "channel_id": 13,
                            "message": f"hello{i}"
                        }).text)
"""

channel = session.get(url=URL + "download_channel",
                      params={"channel_id": str(chan_id)}).json()['channel']

print(channel)

print(session.get(url=URL + "get_user_channel_ids").json())
"""

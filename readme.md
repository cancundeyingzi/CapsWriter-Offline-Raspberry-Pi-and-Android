## CapsWriter-Offline
<img width="462" alt="image" src="https://github.com/cancundeyingzi/CapsWriter-Offline-Raspberry-Pi-and-Android/assets/73635883/56edaec8-da4d-4f84-8d00-cf8e8ab9e16c">        


高效防止反复结束任务，导致后面一句话无法正常识别

改动的地方:

1client_shortcut_handler.py:重点,防止反复结束任务就是在这里改

client_recv_result.py:去掉了打字操作,要的自己再加



附带gotifi调用方法
```
import requests

url = "http://192.168.50.103:1235/message?token=??????????????"
data = {
    "title": "Garage door opened",
    "priority": 5,#重要等级,自己手机上点开通知看
    "message": "11111111111",
    "extras": {
        "client::display": {
            "contentType": "text/plain"  # text/markdown为md文件,里面的网址不能点击
        },
        "client::notification": {
            "click": {"url": "http://baidu.com"} , #点击进入网站
            "bigImageUrl": "https://placekitten.com/400/300"
        }
    }

}

proxies = {"http": None, "https": None}  # proxies代理给他关了
response = requests.post(url=url, proxies=proxies, json=data)
print(response.text)

``

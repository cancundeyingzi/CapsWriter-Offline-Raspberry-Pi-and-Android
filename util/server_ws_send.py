import json
import base64
import asyncio
from multiprocessing import Queue
from datetime import datetime
import requests

from util.server_cosmic import console, Cosmic
from util.server_classes import Result
from util.asyncio_to_thread import to_thread
from rich import inspect


def sendrequest(title, message):
    try:
        url = "http://127.0.0.1:1234/message?token=AJnf-TyO0I8L6_C"
        data = {
            "title": title,
            "message": message,
            "priority": "3"  # 8+,4-7,1-3,0,,,一共四个等级
        }
        proxies = {"http": None, "https": None}  # proxies代理给他关了
        response = requests.post(url=url, proxies=proxies, data=data)
    except:
        sendrequest(title, message)


async def ws_send():
    queue_out = Cosmic.queue_out
    sockets = Cosmic.sockets

    while True:
        try:
            # 获取识别结果（从多进程队列）
            result: Result = await to_thread(queue_out.get)

            # 得到退出的通知
            if result is None:
                return

            # 构建消息
            message = {
                'task_id': result.task_id,
                'duration': result.duration,
                'time_start': result.time_start,
                'time_submit': result.time_submit,
                'time_complete': result.time_complete,
                'tokens': result.tokens,
                'timestamps': result.timestamps,
                'text': result.text,
                'is_final': result.is_final,
            }

            # 获得 socket
            websocket = next(
                (ws for ws in sockets.values() if str(ws.id) == result.socket_id),
                None,
            )

            if not websocket:
                continue

            # 发送消息
            await websocket.send(json.dumps(message))

            if result.source == 'mic':
                print(datetime.now().strftime("%H时%M分%S秒,"), end="")
                console.print(f'某不知名生物：\n    [green]{result.text}')
                sendrequest("某不知名生物消息", result.text)
            elif result.source == 'file':
                console.print(f'    转录进度：{result.duration:.2f}s', end='\r')
                if result.is_final:
                    console.print('\n    [green]转录完成')

        except Exception as e:
            print(e)

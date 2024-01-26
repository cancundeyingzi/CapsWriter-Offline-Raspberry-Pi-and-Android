import asyncio
import json

import keyboard
import websockets
from config import ClientConfig as Config
from util.client_cosmic import Cosmic, console
from util.client_check_websocket import check_websocket
from util.client_hot_sub import hot_sub
from util.client_rename_audio import rename_audio
from util.client_strip_punc import strip_punc
from util.client_write_md import write_md
from util.client_type_result import type_result


async def recv_result():
    if not await check_websocket():
        return
    console.print('[green]连接成功\n')
    try:
        while True:
            message = await Cosmic.websocket.recv()
            message = json.loads(message)
            text = message['text']
            delay = message['time_complete'] - message['time_submit']

            if not message['is_final']:
                continue

            text = strip_punc(text)

            text = hot_sub(text)

            # print ("打字")
            # print await type_result(text)

            if Config.save_audio:
                file_audio = rename_audio(message['task_id'], text, message['time_start'])

                write_md(text, message['time_start'], file_audio)

            console.print(f'    转录时延：{delay:.2f}s')
            console.print(f'    识别结果：[green]{text}')
            console.line()

    except websockets.ConnectionClosedError:
        console.print('[red]连接断开\n')
    except websockets.ConnectionClosedOK:
        console.print('[red]连接断开\n')
    except Exception as e:
        print(e)
    finally:
        return

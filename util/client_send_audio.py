import asyncio
import time

from util.client_cosmic import Cosmic, console
from config import ClientConfig as Config
import numpy as np
import base64
import json
import websockets
from util.client_create_file import create_file
from util.client_write_file import write_file
from util.client_finish_file import finish_file
from util.client_stream import stream_reopen,stream_close #新加
import uuid



async def send_message(message):
    if Cosmic.websocket is None or Cosmic.websocket.closed:
        if message['is_final']:
            Cosmic.audio_files.pop(message['task_id'])
            console.print('    服务端未连接，无法发送\n')
    else:
        try:
            await Cosmic.websocket.send(json.dumps(message))
        except websockets.ConnectionClosedError as e:
            if message['is_final']:
                console.print(f'[red]连接中断了')
        except Exception as e:
            print(e)


async def send_audio():
    try:

        #print ("生成唯一任务 ID")
        task_id = str(uuid.uuid1())

        #print ("任务起始时间")
        time_start = 0

        #print ("音频数据临时存放处")
        cache = []
        duration = 0

        #print ("保存音频文件")
        file_path, file = '', None

        print ("开始取数据")
        # task: {'type', 'time', 'data'}
        while task := await Cosmic.queue_in.get():
            Cosmic.queue_in.task_done()
            print("task['type']是!!!!!!!!!!!!!!!!!!!!!",task['type'],task['time'])
            if task['type'] == 'begin':
                time_start = task['time']
            elif task['type'] == 'data':
                if task['time'] - time_start < Config.threshold:
                    cache.append(task['data'])
                    continue

                if Config.save_audio and not file_path:
                    file_path, file = create_file(task['data'].shape[1], time_start)
                    Cosmic.audio_files[task_id] = file_path

                # print ("获取音频数据")
                if cache:
                    data = np.concatenate(cache)
                    cache.clear()
                else:
                    data = task['data']

                duration += len(data) / 48000
                print (duration,"录音时长duration")
                if Config.save_audio:
                    write_file(file, data)

                #print ("发送音频数据用于识别")
                message = {
                    'task_id': task_id,             # 任务 ID
                    'seg_duration': Config.mic_seg_duration,    # 分段长度
                    'seg_overlap': Config.mic_seg_overlap,      # 分段重叠
                    'is_final': False,              # 是否结束
                    'time_start': time_start,       # 录音起始时间
                    'time_frame': task['time'],     # 该帧时间
                    'source': 'mic',                # 数据来源：从麦克风收到的数据
                    'data': base64.b64encode(       # 数据
                                np.mean(data[::3], axis=1).tobytes()
                            ).decode('utf-8'),
                }
                task = asyncio.create_task(send_message(message))
            elif task['type'] ==  'finish':
                #print ("完成写入本地文件")
                if Config.save_audio:
                    finish_file(file)

                console.print(f'任务标识：{task_id}')
                console.print(f'    录音时长：{duration:.2f}s')
                if duration==0:
                    stream_close(1,2)
                    print("出错尝试重启")

                #print ("告诉服务端音频片段结束了")
                message = {
                    'task_id': task_id,
                    'seg_duration': 15,
                    'seg_overlap': 2,
                    'is_final': True,
                    'time_start': time_start,
                    'time_frame': task['time'],
                    'source': 'mic',
                    'data': '',
                }
                task = asyncio.create_task(send_message(message))
                break
    except Exception as e:
        print(e)
        #print("出问题")

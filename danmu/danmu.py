from curses.textpad import rectangle
from aiowebsocket.converses import AioWebSocket
import json
import asyncio
import zlib
import brotli
import requests
from threading import Thread
import time
from wcwidth import wcswidth
from math import ceil

import curses

danmu_handler = None
gift_handler = None
live_handler = None
preparing_handler = None
other_handler = None
hot_handler = None


class mqueue:
    def __init__(self, maxsize):
        self.items = []
        self.maxsize = maxsize
        self.size = 0

    def push(self, value):
        if not self.full():
            self.items.append(value)
            self.size += 1

    def pop(self) -> str:
        if not self.empty():
            self.size -= 1
            return self.items.pop(0)
        return ''

    def full(self) -> bool:
        if self.size < self.maxsize:
            return False
        return True

    def empty(self) -> bool:
        if self.size == 0:
            return True
        return False


with open('config.json', 'r') as f:
    config = json.load(f)
room_id = config['roomid']


async def start(url: str, roomid: str, outputw: curses.window):
    async with AioWebSocket(url) as aws:
        converse = aws.manipulator

        # 构造进入房间的数据包,数据为json
        '''
        data = {
            "clientver": "1.6.3",
            "platform": "web",
            "protover": 2,
            "roomid": roomid,
            "uid": 0,
            "type": 2
        }
        data = bytes(json.dumps(data), encoding='utf-8')
        header_len = 16  # 长度为2
        protocol_ver = 0  # 长度为2
        op_type = 7  # 长度为4
        reserved = 1  # 长度为4
        data_len = 2 + 2 + 4 + 4 + len(data)
        '''

        data_raw = '{headerLen:08X}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
        data_raw = data_raw.format(headerLen=27 + len(roomid),
                                   roomid=''.join(
                                       map(lambda x: hex(ord(x))[2:],
                                           list(roomid))))
        """ 
        msg = "{data_len:08X}{header_len:04X}{protocol_ver:04X}{op_type:08X}{reserved:08X}".format(
            data_len=data_len,
            header_len=header_len,
            protocol_ver=protocol_ver,
            op_type=op_type,
            reserved=reserved) 
        """
        msg = bytes.fromhex(data_raw)

        await converse.send(msg)

        tasks = asyncio.gather(catch_danmu(converse, outputw),
                               send_heartbeat(converse))
        await tasks


async def catch_danmu(converse, outputw: curses.window):
    while True:
        msg = await converse.receive()
        parse_msg(msg, outputw)


heartbeat_msg = '00000010001000010000000200000001'


async def send_heartbeat(converse):
    while True:
        await asyncio.sleep(25)
        await converse.send(bytes.fromhex(heartbeat_msg))


def parse_msg(msg, outputw: curses.window):
    data_len = int(msg[:4].hex(), 16)
    ver = int(msg[6:8].hex(), 16)
    op_type = int(msg[8:12].hex(), 16)

    # 截断连续收到的数据包
    if (len(msg) > data_len):
        parse_msg(msg[data_len:], outputw)
        msg = msg[:data_len]

    if (ver == 2):
        msg = zlib.decompress(msg[16:])
        parse_msg(msg, outputw)
        return

    if (ver == 3):
        msg = brotli.decompress(msg[16:])
        parse_msg(msg, outputw)
        return

    if (ver == 1 and config['enable']['hot'] == True):
        hot = int(msg[16:20].hex(), 16)
        if hot != 2065851247:
            wprint(outputw, config['format']['hot'].format(hot=hot))
            if hot_handler != None:
                hot_handler(hot=hot)

    if (op_type == 5):
        try:
            jd = json.loads(msg[16:].decode('utf-8', errors='ignore'))
            if (jd['cmd'] == 'DANMU_MSG' and config['enable']['danmu']):
                wprint(
                    outputw,
                    config['format']['danmu'].format(uname=jd['info'][2][1],
                                                     message=jd['info'][1]))
                if danmu_handler != None:
                    danmu_handler(uname=jd['info'][2][1],
                                  message=jd['info'][1])
            elif (jd['cmd'] == 'SEND_GIFT' and config['enable']['gift']):
                wprint(
                    outputw, config['format']['gift'].format(
                        uname=jd['data']['uname'],
                        action=jd['data']['action'],
                        num=jd['data']['num'],
                        giftName=jd['data']['giftName']))
                if gift_handler != None:
                    gift_handler(uname=jd['data']['uname'],
                                 action=jd['data']['action'],
                                 num=jd['data']['num'],
                                 giftName=jd['data']['giftName'])
            elif (jd['cmd'] == 'LIVE' and config['enable']['live']):
                wprint(outputw, config['format']['live'])
                if live_handler != None:
                    live_handler()
            elif (jd['cmd'] == 'PREPARING' and config['enable']['preparing']):
                wprint(outputw, config['format']['preparing'])
                if preparing_handler != None:
                    preparing_handler()
            elif config['enable']['cmd'] == 'True':
                wprint(outputw,
                       config['format']['other'].format(cmd=jd['cmd']))
                if other_handler != None:
                    other_handler(cmd=jd['cmd'])
        except Exception as e:
            pass


def get_real_id(roomid):
    data = requests.get(
        'https://api.live.bilibili.com/room/v1/Room/room_init?id={roomid}'.
        format(roomid=roomid))
    data = json.loads(data.text)
    try:
        return data['data']['room_id']
    except:
        return roomid


send_api_url = 'https://api.live.bilibili.com/msg/send'


def input_thread(inputw: curses.window, roomid: str):
    while True:
        msg = inputw.getstr()
        inputw.clear()

        # send msg
        form = {
            'bubble': '0',
            'msg': msg,
            'color': '16777215',
            'mode': '1',
            'fontsize': '25',
            'rnd': str(int(time.time())),
            'roomid': roomid,
            'csrf': config['csrf'],
            'csrf_token': config['csrf_token'],
        }

        header = {
            'cookie':
            config['cookie'],
            'origin':
            'https://live.bili.com',
            'referer':
            'https://live.bilibili.com/blanc/1029?liteVersion=true',
            'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }

        requests.post(send_api_url, data=form, headers=header)


def wprint(w: curses.window, msg: str):
    w.addstr(msg + '\n')
    w.refresh()


def main(stdscr: curses.window):
    curses.echo()
    curses.nocbreak()

    width = config['size']['width']
    ol = config['size']['output_lines']
    il = config['size']['input_lines']

    real_id = str(get_real_id(room_id))
    output_win = curses.newwin(ol, width, 1, 1)
    output_win.scrollok(True)
    input_win = curses.newwin(il, width, ol + 3, 1)

    rectangle(stdscr, 0, 0, ol + 1, width + 1)
    rectangle(stdscr, ol + 2, 0, ol + 2 + il + 1, width + 1)

    if width > 'Message'.__len__():
        stdscr.addstr(ol + 1, 1, 'Message')

    if width > 'Press Enter'.__len__():
        stdscr.addstr(ol + 2 + il + 1, 1, 'Press Enter')

    stdscr.refresh()
    output_win.refresh()
    input_win.refresh()

    t = Thread(None, input_thread, args=(input_win, real_id))
    t.setDaemon(True)
    t.start()

    asyncio.run(
        start('wss://broadcastlv.chat.bilibili.com:2245/sub', real_id,
              output_win))

    t.join()


def Danmu():
    curses.wrapper(main)


if __name__ == '__main__':
    Danmu()

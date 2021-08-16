from aiowebsocket.converses import AioWebSocket
import json
import asyncio
import zlib
import brotli
import requests

with open('config.json', 'r') as f:
    config = json.load(f)
room_id = config['roomid']

async def start(url: str, roomid: str):
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

        print('start connecting')

        await converse.send(msg)
        tasks = asyncio.gather(catch_danmu(converse), send_heartbeat(converse))
        await tasks


async def catch_danmu(converse):
    while True:
        msg = await converse.receive()
        parse_msg(msg)


heartbeat_msg = '00000010001000010000000200000001'


async def send_heartbeat(converse):
    while True:
        await asyncio.sleep(30)
        await converse.send(bytes.fromhex(heartbeat_msg))


def parse_msg(msg):
    data_len = int(msg[:4].hex(), 16)
    ver = int(msg[6:8].hex(), 16)
    op_type = int(msg[8:12].hex(), 16)

    # 截断连续收到的数据包
    if (len(msg) > data_len):
        parse_msg(msg[data_len:])
        msg = msg[:data_len]

    if (ver == 2):
        msg = zlib.decompress(msg[16:])
        parse_msg(msg)
        return

    if (ver == 3):
        msg = brotli.decompress(msg[16:])
        parse_msg(msg)
        return

    if (ver == 1 and config['verbose'] == 'True'):
        hot = int(msg[16:20].hex(), 16)
        print('当前人气值 : {hot}'.format(hot=hot))

    if (op_type == 5):
        try:
            jd = json.loads(msg[16:].decode('utf-8', errors='ignore'))
            if (jd['cmd'] == 'DANMU_MSG'):
                print(config['format']['danmu'].format(uname=jd['info'][2][1],
                                                       message=jd['info'][1]))
            elif (jd['cmd'] == 'SEND_GIFT'):
                print(config['format']['gift'].format(
                    uname=jd['data']['uname'],
                    action=jd['data']['action'],
                    num=jd['data']['num'],
                    giftName=jd['data']['giftName']))
            elif (jd['cmd'] == 'LIVE'):
                print(config['format']['live'])
            elif (jd['cmd'] == 'PREPARING'):
                print(config['format']['preparing'])
            elif config['verbose'] == 'True':
                print(config['format']['oither'].format(cmd=jd['cmd']))
        except Exception as e:
            pass

def get_real_id(roomid):
    data = requests.get('https://api.live.bilibili.com/room/v1/Room/room_init?id={roomid}'.format(roomid=roomid))
    data = json.loads(data.text)
    try:
        return data['data']['room_id']
    except:
        return room_id

if __name__ == '__main__':
    room_id=str(get_real_id(room_id))
    asyncio.run(start('wss://broadcastlv.chat.bilibili.com:2245/sub', room_id))

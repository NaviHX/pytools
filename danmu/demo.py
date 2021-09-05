import danmu
import pyttsx3
from queue import Queue
from threading import Thread

engine = pyttsx3.init()
engine.setProperty('voice','zh')
engine.setProperty('rate','60')

mq = Queue()

def dh(uname, message, badge=None):
    if uname != 'Navi_Hex':
        mq.put("{uname}说 {message}".format(uname=uname,message=message))

def gh(uname,action,num,giftName):
    mq.put("感谢{uname}{action}的{num}个{giftName}".format(uname=uname,action=action,num=num,giftName=giftName))

def worker(q:Queue):
    while True:
        m = q.get(block=True)
        engine.say(m)
        engine.runAndWait()

dh('弹幕姬','已启动')

t = Thread(None,worker,args=(mq,))
t.setDaemon(True)
t.start()

danmu.danmu_handler=dh
danmu.gift_handler=gh
danmu.Danmu()

#!/usr/local/bin/env python3
import can
import random
import threading
import time

bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
flagIDs = [342, 42, 1337]
myIDs = []


def parse_data(msg):
    myMsg = msg
    sendMsg = []
    if myMsg.arbitration_id == 42:
        sendMsg.append(can.Message(arbitration_id=1337, data=b"ALLES{c4", is_extended_id=False))
        sendMsg.append(can.Message(arbitration_id=1337, data=b"n_sc4n3r", is_extended_id=False))
        sendMsg.append(can.Message(arbitration_id=1337, data=b"}", is_extended_id=False))
    elif myMsg.arbitration_id not in myIDs and myMsg.arbitration_id != 342:
        sendMsg.append(can.Message(arbitration_id=1337, data=b'n0_fl4g', is_extended_id=False))
    for msg in sendMsg:
        bus.send(msg)

def sendFlag1():
    time.sleep(random.uniform(0.1, 0.2))
    with open("flag.png", "rb") as f:
        myByte = f.read(8)
        while myByte != b"":
            msg = can.Message(arbitration_id=342, data=myByte, is_extended_id=False)
            bus.send(msg)
            myByte = f.read(8)

def sendPerdiodicGarbage(canId):
    time.sleep(random.uniform(0.1, 0.2))
    canData = []
    for i in range(0,random.randint(1, 8)):
        canData.append(random.getrandbits(8))
    msg = can.Message(arbitration_id=canId, data=canData, is_extended_id=False)
    bus.send_periodic(msg,random.uniform(0.1, 0.2))

def sendGarbage(canId):
    time.sleep(random.uniform(0.1, 0.2))
    canData = []
    for i in range(0,random.randint(1, 8)):
        canData.append(random.getrandbits(8))
    msg = can.Message(arbitration_id=canId, data=canData, is_extended_id=False)
    bus.send(msg)

myIDs = random.sample(range(2000), k=210)
for i in flagIDs:
    if i in myIDs:
        myIDs.remove(i)
notifier = can.Notifier(bus, [parse_data])
for i in range(100,200):
    tID = myIDs[i]
    t = threading.Thread(target=sendPerdiodicGarbage, args=(tID,))
    t.start()

while True:
    t = threading.Thread(target=sendFlag1)
    t.start()
    for i in range(100):
        tID = myIDs[i]
        t = threading.Thread(target=sendGarbage, args=(tID,))
        t.start()
    time.sleep(random.randint(1,5))

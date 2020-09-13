#!/usr/bin/python3

import string
import hashlib
import base64
import socket
import time

goodHashes = {}

print("Welcome to the \"Doors of Durin\"")
print("I'm the gatekeeper of this ancient place")
print("A long time ago those doors weren't in need of a gatekeeper. But in recent time, especially after the big success of J.R.R. Tolkien, everyone knows the secret words. The passphrase to open the door to the precious flag!")
print("The flag had a lot of visitors and wants to be kept alone. So its my job to keep anyout out")
print("Only real skilled hackers are allowed here. Once you have proven yourself worthy, the flag is yours")

def generateSecretHash(byteInput):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha384()

    blake2b = hashlib.blake2b()

    md5.update(byteInput)
    sha1.update(md5.digest())
    md5.update(sha1.digest())
    
    for i in range(0, 2938):
        sha256.update(md5.digest())

    for k in range(-8222, 1827, 2):
        sha1.update(sha256.digest())
        sha256.update(sha1.digest())

    for j in range(20, 384):
        blake2b.update(sha256.digest())
    
    return blake2b.hexdigest()

def passToGate(byteInput):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("doorsofdurin_door", 1024))
        s.settimeout(1)
        s.sendall(byteInput + b"\n")
        time.sleep(1)
        data = s.recv(1024)
    return data

while True:
    try:
        currentInput = input("Give me your input:")

        bytesInput = base64.b64decode(currentInput)
        print("Doing magic, stand by")
        hashed = generateSecretHash(bytesInput)

        if hashed in goodHashes:
            print(passToGate(bytesInput))
        else:
            if b"sp3akfr1end4nd3nt3r" in bytesInput:
                print("Everybody knows the magic words. I can't hear it anymore! Go away! *smash*")
                exit(0)
            else:
                goodHashes[hashed] = bytesInput
                print(passToGate(bytesInput))

    except Exception as e:
        print(e)
        
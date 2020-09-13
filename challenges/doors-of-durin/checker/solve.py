from pwn import *
import sys
import base64

message1 = open("collision1.bin", "rb").read()
message2 = open("collision2.bin", "rb").read()

p = process(['ncat', '--ssl', sys.argv[1], sys.argv[2]])

p.sendlineafter("Speak friend and enter:", base64.b64encode(message1))
p.sendlineafter("Speak friend and enter:", base64.b64encode(message2))

p.interactive()

# Generated with:
# theuser@DESKTOP-IHD33QF:~/Downloads/hashclash$ scripts/poc_no.sh speakfriend.txt
# theuser@DESKTOP-IHD33QF:~/Downloads/hashclash$ xxd speakfriend.txt
# 00000000: 7370 3361 6b66 7231 656d 6434 6e64 336e  sp3akfr1emd4nd3n
# 00000010: 7433 7200                                t3r.

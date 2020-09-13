import os

ADDR = 0x4014df
os.system("ropper --nocolor --all -f ./graph > rop.txt")
rop = open("rop.txt").read()
gadgets = ""
for l in rop.split("\n"):
    if l[:2] == "0x":
        addr = int(l[:18], 16)
        bits = (addr ^ 0xFFFFFFFFFFFFFFFF) & ADDR
        cnt = bin((ADDR ^ 0xFFFFFFFFFFFFFFFF) & addr).count("1")
        if bits == 0 and cnt < 4:
            gadgets += l + "\n"

open("gadgets.txt", "w").write(gadgets)
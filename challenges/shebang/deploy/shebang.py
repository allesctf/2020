#!/usr/bin/python3 -u
import os
import secrets

NOBODY = 65534
NOGROUP = 65534


def check_input(data):
    if b'.' in data:
        os._exit(1)


def main():
    os.open('/bin/bash', os.O_RDONLY)
    fd = os.open('./flag', os.O_RDONLY)
    os.dup2(fd, 9)

    path = os.path.join('/tmp', secrets.token_hex(16))

    print("#!/d", end="")
    data = os.read(0, 0x10)
    os.close(0)
    check_input(data)

    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o777)
    os.write(fd, b'#!/d' + data)
    os.close(fd)

    pid = os.fork()
    if pid == 0:
        os.setresgid(NOGROUP, NOGROUP, NOGROUP)
        os.setresuid(NOBODY, NOBODY, NOBODY)
        try:
            os.execv(path, [path])
        except:
            os._exit(-1)
    else:
        os.waitpid(pid, 0)
        os.unlink(path)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import sys

pid = int(sys.argv[1], 0)
start = int(sys.argv[2], 0)
end = int(sys.argv[3], 0)

mem_file = open(f"/proc/{pid}/mem", 'rb', 0)
mem_file.seek(start)  # seek to region start
chunk = mem_file.read(end - start)  # read region contents
sys.stdout.buffer.write(chunk)

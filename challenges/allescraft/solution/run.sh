#!/bin/bash
trap 'kill $(jobs -p)' EXIT
echo "Starting python proxy.."
echo "follow the instruction in proxy.lua, you need to expose ports 2337 and 4337"
python3 proxy.py &
echo proxy started
read  -n 1 -p "press any key when the lua proxy started: "
cd pyCraft
python3 ./start.py -u ALLESCTF -o -s 127.0.0.1:4337 -d -f --sip 133.7.133.7 --sid 8526be5c-2c8b-4661-83eb-a160bf9818ec

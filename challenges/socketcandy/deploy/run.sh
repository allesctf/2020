ip link add dev vcan0 type vcan
ip link set up vcan0

python3 chall.py &
socketcand -v -n -p 1024

# docker build -t pwn1 . && docker run -p 1024:1024 --rm -it pwn1

FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3 iputils-ping netcat

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY ynetd .
COPY gatekeeper.py .


RUN chmod +x ynetd gatekeeper.py

RUN chown -R root:root /home/ctf

USER ctf

CMD ./ynetd ./gatekeeper.py
# docker build -t pwn1 . && docker run -p 1024:1024 --rm -it pwn1

FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y gcc

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY flag .
COPY ynetd .
COPY main.c .

RUN gcc main.c -o door

RUN chmod +x ynetd

RUN chown -R root:root /home/ctf

USER ctf

CMD ./ynetd ./door
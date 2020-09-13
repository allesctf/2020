FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3
RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf
COPY ynetd .

COPY LOS7Z9XYZU8YS89Q24PPHMMQFQ3Y7RIE.txt .
COPY pyjail.py .
RUN chmod +x pyjail.py

RUN chown -R root:root /home/ctf

USER ctf

CMD ./ynetd ./pyjail.py
# docker build -t shebang . && docker run -p 1024:1024 -it shebang

FROM ubuntu:20.04

RUN apt-get update && apt-get -y install \
    python3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash ctf
WORKDIR /home/ctf

COPY shebang.py flag ynetd ./
RUN /bin/chown -R root:root ./ \
    && /bin/chmod 0700 ./flag

WORKDIR /home/ctf
CMD ./ynetd ./shebang.py
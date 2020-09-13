FROM debian:latest

RUN apt-get update && \
  apt-get install -y python3 python3-can can-utils build-essential autoconf git

WORKDIR /challenge

RUN git clone https://github.com/linux-can/socketcand.git && \
  cd socketcand && \
  ./autogen.sh && \
  ./configure && \
  make && make install

COPY flag.png .
COPY chall.py .
COPY run.sh .

RUN chmod a+x run.sh

CMD ./run.sh

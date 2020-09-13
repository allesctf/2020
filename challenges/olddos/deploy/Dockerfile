FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install \
    golang coreutils dosfstools \
    && rm -rf /var/lib/apt/lists/*

COPY flag_file.txt main.go list.gohtml show.gohtml run.sh ./

RUN go build main.go && chmod a+x run.sh

CMD ./run.sh

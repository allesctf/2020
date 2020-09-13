FROM debian:stretch-slim
LABEL maintainer="riku.lindblad@gmail.com"

RUN apt-get update && apt-get -y install \ 
    python \
    python-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

#RUN git clone https://github.com/lepinkainen/pyfibot.git /pyfibot

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

RUN mkdir /bot
COPY ./pyfibot /bot

RUN chmod -R 777 /bot
RUN chown -R ctf:ctf /bot

WORKDIR /bot

RUN pip install pipenv
RUN pipenv install --system

USER ctf
WORKDIR /bot

COPY ./config.yml /bot/config.yml
ADD ./additional_modules /bot/pyfibot/modules/


CMD ["/bin/sh", "-c", "sleep 5; python /bot/pyfibot/pyfibot.py /bot/config.yml"]



FROM alpine:latest

ENV MINECRAFT_RAM="4096"
ENV MINECRAFT_VERSION="forge-1.12.2-14.23.5.2854"

ARG OC_VERSION="v1.7.5"
ARG OC_VERSION_LONG="MC1.12.2-1.7.5.192"

COPY minecraft.py /home/minecraft/minecraft.py
COPY run.sh /home/minecraft/run.sh
COPY options.txt /home/minecraft/.minecraft/options.txt
COPY servers.dat /home/minecraft/.minecraft/servers.dat

RUN set -x && \
	apk add --no-cache libxcursor mesa-dri-gallium openal-soft openjdk8-jre \
	    py3-pip python3 wget x11vnc xrandr xvfb xvfb-run && \
	cd /home/minecraft && \
	PYTHONUNBUFFERED=1 python3 minecraft.py install ${MINECRAFT_VERSION} /home/minecraft && \
	ln -sfT /usr/lib/libopenal.so .minecraft/bin/natives/libopenal.so && \
	ln -sfT /usr/lib/libopenal.so .minecraft/bin/natives/libopenal64.so && \
	mkdir /home/minecraft/.minecraft/mods && \
	cd /home/minecraft/.minecraft/mods && \
	wget https://github.com/MightyPirates/OpenComputers/releases/download/${OC_VERSION}/OpenComputers-${OC_VERSION_LONG}.jar && \
	cd /home/minecraft && \
    addgroup minecraft && \
	adduser -D -h /home/minecraft -H -G minecraft minecraft && \
	chown -R minecraft:minecraft /home/minecraft && \
	chmod a+x /home/minecraft/run.sh && \
	rm -rf /home/minecraft/logs && \
	rm -rf /home/minecraft/*.log

USER minecraft
WORKDIR /home/minecraft
CMD ['/home/minecraft/run.sh']

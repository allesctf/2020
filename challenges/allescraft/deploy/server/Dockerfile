FROM ubuntu:bionic as runtime

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
ENV JAVA_HOME=/usr/lib/jvm/zulu-8-amd64

RUN set -x && \
	# Install zulu java
	apt-get -qq update && \
	apt-get -qq -y --no-install-recommends install \
		gnupg software-properties-common locales && \
	locale-gen en_US.UTF-8 && \
	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9 && \
	apt-add-repository "deb http://repos.azulsystems.com/ubuntu stable main" && \
	apt-get -qq update && \
	apt-get -qq -y dist-upgrade && \
	apt-get -qq -y --no-install-recommends install zulu-8=8.46.0.19 && \
	# Install other requirements and create user
	apt-get -qq -y --no-install-recommends install wget && \
	useradd allescraft && \
	rm -rf /var/lib/apt/lists/*

# Now build the plugin
FROM runtime AS build-env
RUN set -x && \
	apt-get -qq update && \
	apt-get -qq -y --no-install-recommends install build-essential maven

COPY getflag.c /
COPY plugin /plugin
RUN set -x && \
	gcc -o /getflag /getflag.c && \
	cd /plugin/Flag && \
	mvn package


# Copy the server configuration and plugin
FROM runtime

ARG FORGE_VERSION="1.12.2-14.23.5.2854"
ARG SPONGE_VERSION="1.12.2-2838-7.2.3"
ARG OC_VERSION="v1.7.5"
ARG OC_VERSION_LONG="MC1.12.2-1.7.5.192"

COPY flag /flag
COPY forge /forge
COPY world /forge/world
COPY --from=build-env /plugin/Flag/target/flag-0.0.1-SNAPSHOT.jar /forge/mods/plugins/
COPY --from=build-env /getflag /

# Install forge and additional mods
RUN set -x && \
	cd /forge && \
	wget -O forge-installer.jar https://files.minecraftforge.net/maven/net/minecraftforge/forge/${FORGE_VERSION}/forge-${FORGE_VERSION}-installer.jar && \
	java -jar forge-installer.jar --installServer && \
	mv forge-${FORGE_VERSION}.jar forge.jar && \
	cd /forge/mods && \
	wget https://repo.spongepowered.org/maven/org/spongepowered/spongeforge/${SPONGE_VERSION}/spongeforge-${SPONGE_VERSION}.jar && \
	wget https://github.com/MightyPirates/OpenComputers/releases/download/${OC_VERSION}/OpenComputers-${OC_VERSION_LONG}.jar && \
	chown -R allescraft /forge /flag && \
	chown root:root /getflag /flag && \
	chmod +s /getflag && \
	chmod 400 /flag

WORKDIR /forge
USER allescraft

CMD java -Xms512m -Xmx512m -jar forge.jar nogui

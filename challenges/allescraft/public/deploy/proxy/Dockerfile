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
	apt-get update && \
	apt-get -qq -y --no-install-recommends install maven

COPY plugin /plugin
RUN set -x && \
	cd /plugin/ALLESQueue && \
	mvn package

# Copy the server configuration and plugin
FROM runtime

ARG FORGE_VERSION="1.12.2-14.23.5.2854"
ARG SPONGE_VERSION="1.12.2-2838-7.2.3"
ARG OC_VERSION="v1.7.5"
ARG OC_VERSION_LONG="MC1.12.2-1.7.5.192"

COPY bungeecord /bungeecord
COPY --from=build-env /plugin/ALLESQueue/target/queue-0.0.1-SNAPSHOT.jar /bungeecord/plugins/

# Install bungeecord
RUN set -x && \
	cd /bungeecord && \
	wget https://papermc.io/ci/job/Waterfall/lastSuccessfulBuild/artifact/Waterfall-Proxy/bootstrap/target/Waterfall.jar && \
	chown -R allescraft /bungeecord

WORKDIR /bungeecord
USER allescraft

CMD java -jar Waterfall.jar

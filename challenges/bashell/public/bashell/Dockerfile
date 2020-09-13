# docker build -t bashell . && docker run -p 1024:1024 --mount type=tmpfs,destination=/tmp --rm bashell
FROM alpine:latest as buildenv

RUN set -x && \
	apk add --no-cache curl g++ libcap-dev libcap-static make tar

ARG CC="gcc"
ARG CFLAGS="-static -Os"

WORKDIR /build
RUN set -x && \
	curl -LO http://ftp.gnu.org/gnu/bash/bash-5.0.tar.gz && \
	tar -xf bash-5.0.tar.gz && \
	cd bash-5.0 && \
	./configure --without-bash-malloc && \
	make

RUN set -x && \
	curl -LO https://yx7.cc/code/ynetd/ynetd-0.1.2.tar.xz && \
	tar -xf ynetd-0.1.2.tar.xz && \
	cd ynetd-0.1.2 && \
	make

COPY init.sh /init.sh
COPY flag /flag
COPY fuckmypidup.c /fuckmypidup.c

RUN set -x && \
	${CC} -static -O3 -no-pie /fuckmypidup.c -lcap -o /fuckmypidup

RUN set -x && \
	chmod 444 /flag && \
	chmod 555 /init.sh /fuckmypidup /build/bash-5.0/bash \
		/build/ynetd-0.1.2/ynetd

FROM scratch
USER 1000

COPY --from=buildenv --chown=0:0 /flag /flag
COPY --from=buildenv --chown=0:0 /init.sh /init.sh
COPY --from=buildenv --chown=0:0 /fuckmypidup /fuckmypidup
COPY --from=buildenv --chown=0:0 /build/bash-5.0/bash /bin/bash
COPY --from=buildenv --chown=0:0 /build/ynetd-0.1.2/ynetd /ynetd

# remote: (just randomizes your pid) ENTRYPOINT ["/ynetd", "-sh", "n", "/fuckmypidup"]
ENTRYPOINT ["/ynetd", "-sh", "n", "/init.sh"]
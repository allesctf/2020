FROM fedora:32

RUN dnf install -y dnf-plugins-core git cmake ninja-build zstd tar curl patch && dnf builddep -y rr
RUN curl -L https://github.com/mozilla/rr/archive/5.3.0.tar.gz | tar xz
COPY rr.patch /rr-5.3.0/rr.patch
RUN cd /rr-5.3.0 && patch -p1 < rr.patch && cmake . -G Ninja -Ddisable32bit=ON && ninja && ninja install

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY cat .
COPY flag .
COPY experiment.sh .
COPY ynetd .

RUN chmod +x ./ynetd ./cat ./experiment.sh
USER ctf

CMD ./ynetd ./experiment.sh

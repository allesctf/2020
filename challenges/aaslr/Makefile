CC=gcc
CFLAGS=

all: aaslr

aaslr: public/aaslr.c
	$(CC) public/aaslr.c -o public/aaslr
	cp public/Dockerfile deploy/Dockerfile
	cp public/aaslr deploy/aaslr
	echo "ALLES{FLAG_GUESS}" > public/flag1
	echo "ALLES{FLAG_PWN}" > public/flag2
	cp public/flag1 deploy/flag1
	cp public/flag2 deploy/flag2

clean:
	rm public/aaslr deploy/aaslr deploy/flag1 deploy/flag2 public/flag1 public/flag2


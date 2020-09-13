// gcc -pie cat.c -o cat

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

typedef void poison(void);

int main(int argc, char** argv) {
    if (argc != 2) {
        puts("usage: cat POISON");
        return 1;
    }

    srand(time(NULL));
    poison* die = (poison*)strtoul(argv[1], NULL, 0);

    char buf[1024];
    while (1) {
        int count = read(0, buf, sizeof(buf));
        if (count < 0) {
            perror("read");
            return 1;
        }
        if (count == 0) break;

        int written = 0;
        while (written < count) {
            written += write(1, &buf[written], count - written);
        }

        if (rand() % 10 == 0) {
            /* the poison kills the cat, because we built with PIE */
            die();
        }
    }
}

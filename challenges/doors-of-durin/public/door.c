#include<stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <unistd.h>

#define MAGIC_WORD "sp3akfr1end4nd3nt3r"
int main() {
    char input[255];
    char flag[255];

    scanf("%254s", input);
	printf("You said: %s\n", input);

    if (strcmp(input, MAGIC_WORD) == 0)
    {
        int fd = open("./flag", O_RDONLY);
        if (fd == -1)
        {
            printf("Something went wrong! Thats a bug, please report!\n");
            return 1;
        }

        read(fd, flag, 254);
        printf("Flag: %s\n", flag);
    }
    else
    {
        printf("Nope :/\n");
    }
    
	return 0;
}
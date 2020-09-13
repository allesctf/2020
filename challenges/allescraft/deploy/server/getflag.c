#include <unistd.h>
#include <stdlib.h>

void main(void)
{
	setreuid(geteuid(), getuid());
	setregid(getegid(), getgid());

	system("/bin/cat /flag");
}

#include <sys/resource.h>

#include <err.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


static int check(int res, const char *msg)
{
	if (res == -1)
		err(1, "%s", msg);
	return res;
}

int main(int argc, char **argv)
{
	if (argc < 2) {
		fprintf(stderr, "USAGE %s <program> [args]\n", argv[0]);
	}

	struct rlimit rlimit = {
		.rlim_cur = 200,
		.rlim_max = 200
	};

	/*
	check(setrlimit(RLIMIT_NPROC, &rlimit),
	      "Could not set rlimit");
	*/

	execv(argv[1], &argv[1]);
	err(1, "execve failed");
}

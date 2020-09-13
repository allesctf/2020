/**
 * This program just - as the name might suggest - fucks your pid up.
 *
 * It's only here to make your life worse and regret going to bashell.
 *
 * You can safely ignore this small helper program as it's not part of the
 * challenge, but of the setup.
 */
#define _GNU_SOURCE

#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/capability.h>

#include <err.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifdef DEBUG
static const int debug = 1;
#else
static const int debug = 0;
#endif

static int check(int res, const char *msg)
{
	if (res == -1)
		err(1, "%s", msg);
	return res;
}

uint32_t get_max_pid()
{
	int fd, num;
	char max_pid[32];
	uint32_t max;

	fd = check(open("/proc/sys/kernel/pid_max", O_RDONLY, 0444),
		   "Could not open maximum pid");

	num = check(read(fd, max_pid, 31),
		    "Could not read maximum pid");
	max_pid[num] = 0;

	max = strtoul(max_pid, NULL, 10);
	check(close(fd), "Could not close maximum pid");
	return max;
}

uint32_t get_random_pid(uint32_t min_val, uint32_t max_val)
{
	int fd;
	uint32_t next_pid = 0;

	fd = check(open("/dev/urandom", O_RDONLY, 0444),
		   "Could not open random device");

	while (next_pid < min_val || next_pid > max_val) {
		check(read(fd, &next_pid, 4),
		      "Could not read random value");

		next_pid %= max_val + 1;
	}

	check(close(fd), "Could not close random device");
	return next_pid;
}

static void drop_caps()
{
	cap_t caps = cap_init();
	check(cap_set_proc(caps), "Could not drop capabilities");
	cap_free(caps);
}

static int setup_sandbox(int min_pid, int pipe)
{
	int fd, child_pid;
	char pid[8];
	char dummy = 0xff;
	uint32_t max_pid = get_max_pid();

	/* Wait for our uid/gid mapping to be established */
	check(read(pipe, &dummy, 1),
	      "Could not wait for parent to map uid/gid");

	/* Remount the procfs as we still have the old one */
	check(mount("none", "/proc", NULL, MS_PRIVATE | MS_REC, NULL),
	      "Could not unmount /proc");
	check(mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV,
		    NULL),
	      "Could not mount /proc");

	/* Set the next pid */
	snprintf(pid, 8, "%u", get_random_pid(min_pid, max_pid - 1) - 1);
	fd = check(open("/proc/sys/kernel/ns_last_pid", O_WRONLY),
		   "Could not open ns_last_pid");
	check(write(fd, pid, strlen(pid)), "Could not write ns_last_pid");
	check(close(fd), "Could not close ns_last_pid");

	child_pid = check(fork(), "Could not fork sandbox process");

	if (!child_pid) {
		/*
		 * We are at our desired pid, just drop all caps and execvpe.
		 *
		 * NOTE: We *are* uid 0, but this is a namespace with uid 0
		 * mapped to the calling uid - so there's no need to care.
		 */
		drop_caps();

		char *argv[2] = {
			"/init.sh",
			0
		};

		execvpe(argv[0], argv, NULL);
		return 0;
	}

	check(waitpid(child_pid, NULL, 0),
	      "Error waiting on sandbox child to exit");

	return 0;
}

static void write_ns_mapping(int pid, char *type, char *mapping)
{
	int fd;
	char filename[256];

	snprintf(filename, 256, "/proc/%u/%s", pid, type);
	fd = check(open(filename, O_RDWR, 0666),
		   "Could not open mapping");

	check(write(fd, mapping, strlen(mapping)),
	      "Could not write mapping");
	check(close(fd), "Could not close mapping");
}

int main(void)
{
	/* Disable IO buffering */
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	char dummy = 0xff;
	char uid_mapping[32];
	char gid_mapping[32];

	uid_t our_uid = geteuid();
	gid_t our_gid = getegid();

	snprintf(uid_mapping, 32, "0 %u 1\n", our_uid);
	snprintf(gid_mapping, 32, "0 %u 1\n", our_gid);

	int pipes[2];
	check(socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, pipes),
	      "Could not create socketpair");

	/* Setup sandbox */
	uint32_t sandbox_pid = check(
		syscall(SYS_clone,
			CLONE_NEWUSER | CLONE_NEWPID | CLONE_NEWNS |
			CLONE_NEWNET | SIGCHLD, 0, 0, 0, 0),
		"Creating sandbox failed");

	if (!sandbox_pid)
		return setup_sandbox(13337, pipes[1]);

	/* Setup user/group mapping */
	write_ns_mapping(sandbox_pid, "setgroups", "deny");
	write_ns_mapping(sandbox_pid, "uid_map", uid_mapping);
	write_ns_mapping(sandbox_pid, "gid_map", gid_mapping);
	check(write(pipes[0], &dummy, 1), "Could not signal child");

	if (debug)
		printf("Sandbox spawned with pid: %u\n", sandbox_pid);

	/* Wait for sandbox to exit */
	check(waitpid(sandbox_pid, NULL, 0),
	      "Error waiting on sandbox to exit");

	if (debug)
		puts("Sandbox done, exiting.");
	return 0;
}

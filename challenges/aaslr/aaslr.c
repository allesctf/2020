#include <time.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <sys/mman.h>

#define HEAP_SIZE (0xffff+1)
char* HEAP = NULL;
int ENTRIES = 0;
#define MAX_ENTRIES 0xff
#define MAX_ENTRY_LEN 100
char* *ENTRY;


// --------------------------------------------------- RANDOM
// https://burtleburtle.net/bob/rand/smallprng.html

typedef unsigned long int u8;
typedef struct ranctx { u8 a; u8 b; u8 c; u8 d; } ranctx;
ranctx RANCTX;

#define rot(x,k) (((x)<<(k))|((x)>>(32-(k))))

u8 ranval() {
	ranctx *x = &RANCTX;
    u8 e = x->a - rot(x->b, 27);
    x->a = x->b ^ rot(x->c, 17);
    x->b = x->c + x->d;
    x->c = x->d + e;
    x->d = e + x->a;
    return x->d;
}

void raninit(u8 seed ) {
	ranctx *x = &RANCTX;
    u8 i;
    x->a = 0xf1ea5eed, x->b = x->c = x->d = seed;
    for (i=0; i<20; ++i) {
        (void)ranval(x);
    }
}


// --------------------------------------------------- SETUP

void init_buffering() {
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
}

void kill_on_timeout(int sig) {
  if (sig == SIGALRM) {
  	printf("[!] Anti DoS Signal. Patch me out for testing.");
    _exit(0);
  }
}

void init_signal() {
	signal(SIGALRM, kill_on_timeout);
	alarm(60);
}

size_t read_input(int fd, char *buf, size_t size) {
  size_t i;
  for (i = 0; i < size-1; ++i) {
    char c;
    if (read(fd, &c, 1) <= 0) {
      _exit(0);
    }
    if (c == '\n') {
      break;
    }
    buf[i] = c;
  }
  buf[i] = '\0';
  return i;
}


// --------------------------------------------------- HEAP

void init_heap() {
	time_t now;
	HEAP = mmap(NULL, HEAP_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	now = time(NULL);
	raninit(now);
}

char* aaslr_malloc(size_t size) {
	char* addr = NULL;
	if(HEAP == NULL) {
		init_heap();
	} 
	if(HEAP != NULL) {
		addr = HEAP+(ranval() % (HEAP_SIZE-size));
	} else {
		_exit(0);
	}
	return addr;
}

void aaslr_free(char* ptr) {
	// Randomness is true freedom. The chains of allocations are GONE!
}


// --------------------------------------------------- MENU

void print_menu(){
	printf(
		"Welcome To The Actual-ASLR (AASLR) Demo\n"
		"  1. throw dice\n"
		"  2. create entry\n"
		"  3. read entry\n"
		"  4. take a guess\n"
		"\n"
		"Select menu Item:\n");
}

int throw_dice() {
	return (ranval()%6)+1;
}


int create_entry() {
	if(ENTRIES >= MAX_ENTRIES) {
		printf("[!] You reached the maximum entries for this demo license. Exiting now.");
		_exit(0);
	}
	
	ENTRY[ENTRIES] = aaslr_malloc(MAX_ENTRY_LEN);
	
	char read_buf[MAX_ENTRY_LEN];
	printf("Enter your data (max length: %d):\n", MAX_ENTRY_LEN);
	memset(read_buf, 0, sizeof(read_buf));
	read_input(0, read_buf, sizeof(read_buf));
	memcpy(ENTRY[ENTRIES], read_buf, sizeof(read_buf));

	return ENTRIES++;
}

void read_entry() {
	if(ENTRIES<=0) {
		printf("[!] Please create an entry first.\n");
		return;
	}

	printf("Enter entry index (max: %d):\n", ENTRIES-1);

	char read_buf[0xff];
	memset(read_buf, 0, sizeof(read_buf));
	read_input(0, read_buf, sizeof(read_buf));
	int index = atoi(read_buf);

	printf("[>] %d. %s\n", index, ENTRY[index]);
}

void error_case(char* msg) {
	printf("[!] Couldn't understand \"%s\"\n", msg);
}

void take_guess() {
	char read_buf[0xff];

	int correct_guesses = 0;
	for(int i=0; i<0xf; i++) {
		printf("(%d/16) guess next dice roll:\n", i+1);
		memset(read_buf, 0, sizeof(read_buf));
		read_input(0, read_buf, sizeof(read_buf));
		int guessed_dice = atoi(read_buf);
		int dice = throw_dice();

		if(guessed_dice == dice) {
			correct_guesses++;
		} 
	}
	if(correct_guesses == 0xf) {
		printf("[>] CORRECT! You should go to Vegas.\n");
		system("cat flag1");
	} else {
		printf("[!] WRONG!\n");
	}
}

struct menu_handler {
  int (*throw_dice)(void);
  int (*create_entry)(void);
  void (*read_entry)(void);
  void (*take_guess)(void);
  void (*error_case)(char*);
};


// --------------------------------------------------- MAIN

int main(int argc, char* argv[]) {
	
	init_buffering();
	init_signal();

	struct menu_handler* handle;
	handle = (struct menu_handler *)aaslr_malloc(sizeof(struct menu_handler));
	handle->throw_dice = throw_dice;
	handle->create_entry = create_entry;
	handle->read_entry = read_entry;
	handle->take_guess = take_guess;
	handle->error_case = error_case;
	ENTRY = (char**) aaslr_malloc(sizeof(ENTRY) * MAX_ENTRIES);

	// menu loop
	char read_buf[0xff];
	for(;;) {
		print_menu();
		memset(read_buf, 0, sizeof(read_buf));
		read_input(0, read_buf, sizeof(read_buf));
		if(strcmp(read_buf, "1") == 0) {
			int value = handle->throw_dice();
			printf("[>] Threw dice: %d\n", value);
		} else if(strcmp(read_buf, "2") == 0) {
			int index = handle->create_entry();
			printf("[>] Created new entry at index %d\n", index);
		} else if(strcmp(read_buf, "3") == 0) {
			handle->read_entry();
		} else if(strcmp(read_buf, "4") == 0) {
			handle->take_guess();
		} else {
			handle->error_case(read_buf);
		}
	}
}



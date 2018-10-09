#include <stdio.h>
#include <unistd.h>
#include <time.h>

typedef int bool;
#define TRUE  1
#define FALSE 0


void mainloop() {
    FILE *file;
    char current_key[8], prev_key[8];
    long key_nsec, prev_nsec;
    struct timespec spec;
    bool keydown = FALSE;

    file = fopen("/var/run/keys", "r");

    if (!file) {
        return;
    }

    while (TRUE) {
        clock_gettime(CLOCK_REALTIME, &spec);
        fscanf(file, "%s\n", current_key);
        fscanf(file, "%ld\n", &key_nsec);

        if (keydown && (spec.tv_nsec - key_nsec) >= 25e7) {
            system("DISPLAY=:0 xte keyup " + prev_key);
            prev_nsec = spec.tv_nsec;
            keydown = FALSE;
        }

        if (strcmp(current_key, prev_key) != 0 || (!keydown && prev_nsec != key_nsec)) {
            system("DISPLAY=:0 xte keyup " + prev_key)
            system("DISPLAY=:0 xte keydown " + current_key)
            keydown = TRUE;
        }

        strncpy(prev_key, current_key, 8);

        fseek(file, 0, SEEK_SET);
        usleep(20000);
    }
}


int main(int argc, char *argv[]) {
  if (argc > 1 && argv[1] == "-n") {
      mainloop();
      exit(0);
  }
  int pid = fork();
  switch(pid) {
  case 0:
    setsid();
    chdir("/");
    close(stdin);
    close(stdout);
    close(stderr);
    mainloop();
    exit(0);
  case -1:
    printf("Fail: unable to fork\n");
    break;
  default:
   printf("OK: demon with pid %d is created\n", pid);
   break;
 }
 return 0;
}

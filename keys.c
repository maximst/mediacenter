#include <stdio.h>
#include <unistd.h>
#include <time.h>

typedef int bool;
#define TRUE  1
#define FALSE 0


void mainloop() {
    FILE *file;
    char current_key[8], prev_key[8], cmd[32];
    long key_sec, key_nsec, *prev_nsec;
    struct timespec spec;
    bool keydown = FALSE;

    file = fopen("/var/run/keys", "r");

    if (!file) {
        return;
    }

    while (TRUE) {
        clock_gettime(CLOCK_REALTIME, &spec);
        fscanf(file, "%s\n", current_key);
        fscanf(file, "%ld\n", &key_sec);
        fscanf(file, "%ld\n", &key_nsec);

        if (keydown && ((spec.tv_sec - key_nsec) >= 373e6 || (spec.tv_sec > key_sec && key_nsec < 620e6))) {
            printf("1: %ld %ld\n", spec.tv_nsec, key_nsec);
            sprintf(cmd, "DISPLAY=:0 xte 'keyup %s' #1\n", prev_key);
            printf(cmd);
            system(cmd);
            prev_nsec = key_nsec;
            keydown = FALSE;
        }

        if ((strcmp(current_key, prev_key) != 0) || (!keydown && prev_nsec != key_nsec)) {
            printf("2: %ld %ld\n", prev_nsec, key_nsec);
            sprintf(cmd, "DISPLAY=:0 xte 'keyup %s' #2\n", prev_key);
            printf(cmd);
            system(cmd);
            keydown = TRUE;
            sprintf(cmd, "DISPLAY=:0 xte 'keydown %s' #3\n", current_key);
            printf(cmd);
            system(cmd);
        }

        strncpy(prev_key, current_key, 8);

        fseek(file, 0, SEEK_SET);
        usleep(19763);
    }
}


int main(int argc, char *argv[]) {
    mainloop();
    exit(0);
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

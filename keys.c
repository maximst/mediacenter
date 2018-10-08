#include <stdio.h>
#include <unistd.h>
#include <time.h>

typedef int bool;
#define TRUE  1
#define FALSE 0


float get_time() {
    struct timespec spec;
    float cur_time = 0.0;
    clock_gettime(CLOCK_REALTIME, &spec);
    cur_time = difftime(spec.tv_sec, 0) + ((float)spec.tv_nsec / 1e9);
    return cur_time;
}


void mainloop() {
    FILE *file;
    char current_key[8], prev_key[8];
    float key_time, current_time;
    struct timespec spec;
    bool keydown = FALSE;

    file = fopen("/var/run/keys", "r");

    if (!file) {
        return;
    }

    while (TRUE) {
        clock_gettime(CLOCK_REALTIME, &spec);
        fscanf(file, "%s\n", current_key);
        fscanf(file, "%f\n", &key_time);
        printf("kt %f\n", (float)key_time);

        //printf("%f\n", difftime(spec.tv_sec, 0) + ((float)spec.tv_nsec / 1e9));
        if (keydown && ((difftime(spec.tv_sec, 0) + ((float)spec.tv_nsec / 1e9)) - key_time) >= 0.25) {
            //system("DISPLAY=:0 xte keyup " + prev_key)
            printf("0000000\n");
            printf("DISPLAY=:0 xte keyup %s\n", prev_key);
            printf("1111111\n");
            keydown = FALSE;
            printf("2222222\n");
            printf(" 1 %f %f\n", (difftime(spec.tv_sec, 0) + ((float)spec.tv_nsec / 1e9)), key_time);
        }

        if (strcmp(current_key, prev_key) != 0 || (!keydown && ((difftime(spec.tv_sec, 0) + ((float)spec.tv_nsec / 1e9)) - key_time) < 0.25)) {
            //system("DISPLAY=:0 xte keyup " + prev_key)
            printf("DISPLAY=:0 xte keyup %s\n", prev_key);
            //system("DISPLAY=:0 xte keydown " + current_key)
            printf("DISPLAY=:0 xte keydown %s\n", current_key);
            printf(" 2 %f %f\n", (difftime(spec.tv_sec, 0) + ((float)spec.tv_nsec / 1e9)), key_time);
            keydown = TRUE;
        }

        //prev_key = current_key;
        strncpy(prev_key, current_key, 8);

        fseek(file, 0, SEEK_SET);
        usleep(20000);
    }
}


int main(int argc, char *argv[]) {
  mainloop();
  exit(0);
  if (argc > 1 && argv[1] == "-n") {
      printf("AAAAAAAAa");
      mainloop();
      printf("BBBBBBBBBBB");
      exit(0);
      printf("CCCCCCCCC");
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

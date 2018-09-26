#include <stdio.h>
#include <unistd.h>
#include <time.h>


void mainloop() {
    FILE *file;
    char current_key[6], prev_key[6];
    float key_time, current_time;
    struct spec;

    file = fopen("/var/run/keys", "r");

    if (!file) {
        return;
    }

    while (1) {
        fscanf(file, "%s\n", current_key);
        fscanf(file, "%f\n", &key_time);

        clock_gettime(CLOCK_REALTIME, &spec);
        current_time = spec.tv_sec + (spec.tv_nsec / 1e9);

        if ((current_time - key_time) > 0.5) {
            //TODO: prev_key Up
        }

        if (current_key != prev_key) {
            //TODO: prev_key Up
            //TODO: current_key Down
        }

        prev_key = current_key;

        fseek(file, 0, SEEK_SET);
        usleep(20000);
    }
}


int main() {
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

#include <stdio.h>
#include <unistd.h>
#include <time.h>

typedef int bool;
#define TRUE  1
#define FALSE 0

#define UP 0
#define RIGHT 1
#define DOWN 2
#define LEFT 3
#define RETURN 4
#define ESCAPE 5
#define MENU 6
#define _2NDFX 7


void mainloop() {
    int current_key, prev_key, _2ndfx = 0;
    FILE *file;
    long key_sec, key_nsec, *prev_nsec;
    struct timespec spec;
    bool keydown = FALSE;
    const char *keys[8][2][48] = {
        {"DISPLAY=:0 xte 'keydown Up'\n", "DISPLAY=:0 xte 'keyup Up'\n"},
        {"DISPLAY=:0 xte 'keydown Right'\n", "DISPLAY=:0 xte 'keyup Right'\n"},
        {"DISPLAY=:0 xte 'keydown Down'\n", "DISPLAY=:0 xte 'keyup Down'\n"},
        {"DISPLAY=:0 xte 'keydown Left'\n", "DISPLAY=:0 xte 'keyup Left'\n"},
        {"DISPLAY=:0 xte 'keydown Return'\n", "DISPLAY=:0 xte 'keyup Return'\n"},
        {"DISPLAY=:0 xte 'keydown Escape'\n", "DISPLAY=:0 xte 'keyup Escape'\n"},
        {"DISPLAY=:0 xte 'keydown Control_L' 'keydown M'\n", "DISPLAY=:0 xte 'keyup M' 'keyup Control_L'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Up'\n", "DISPLAY=:0 xte 'keyup KP_Up'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Right'\n", "DISPLAY=:0 xte 'keyup KP_Right'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Down'\n", "DISPLAY=:0 xte 'keyup KP_Down'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Left'\n", "DISPLAY=:0 xte 'keyup KP_Left'\n"},
        {"DISPLAY=:0 xte 'keydown Return'\n", "DISPLAY=:0 xte 'keyup Return'\n"},
        {"DISPLAY=:0 xte 'keydown Escape'\n", "DISPLAY=:0 xte 'keyup Escape'\n"},
        {"DISPLAY=:0 xte 'keydown Control_L' 'keydown M'\n", "DISPLAY=:0 xte 'keyup M' 'keyup Control_L'\n"},
    };

    file = fopen("/var/run/keys", "r");

    if (!file) {
        return;
    }

    while (TRUE) {
        clock_gettime(CLOCK_REALTIME, &spec);
        fscanf(file, "%i\n", current_key);
        fscanf(file, "%ld\n", &key_sec);
        fscanf(file, "%ld\n", &key_nsec);

//        printf("QQQQ: %i %ld %ld\n", keydown, spec.tv_nsec, key_nsec);
        if (keydown && ((spec.tv_nsec - key_nsec) >= 283e6 || (spec.tv_sec > key_sec && spec.tv_nsec > 273e6))) {
            if (current_key == _2NDFX) {
                _2ndfx = abs(_2ndfx - _2NDFX);
            } else {
                printf("1: %ld %ld\n", spec.tv_nsec, key_nsec);
                //sprintf(cmd, "DISPLAY=:0 xte 'keyup %s' #1\n", prev_key);
                printf(keys[current_key + _2ndfx][1]);
                system(keys[current_key + _2ndfx][1]);
            }
            prev_nsec = key_nsec;
            keydown = FALSE;
        }

        if ((strcmp(current_key, prev_key) != 0) || (!keydown && prev_nsec != key_nsec)) {
            printf("2: %ld %ld\n", prev_nsec, key_nsec);
            //sprintf(cmd, "DISPLAY=:0 xte 'keyup %s' #2\n", prev_key);
            printf(keys[prev_key + _2ndfx][1]);
            system(keys[prev_key + _2ndfx][1]);
            keydown = TRUE;
            //sprintf(cmd, "DISPLAY=:0 xte 'keydown %s' #3\n", current_key);
            printf(keys[current_key + _2ndfx][0]);
            system(keys[current_key + _2ndfx][0]);
        }

        prev_key = current_key;
        //strncpy(prev_key, current_key, 8);

        fseek(file, 0, SEEK_SET);
        usleep(19753);
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

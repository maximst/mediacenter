#include <stdio.h>
#include <unistd.h>
#include <time.h>

typedef int bool;
#define TRUE  1
#define FALSE 0

#define _2NDFX 10


void mainloop() {
    int current_key, prev_key, _2ndfx = 0;
    FILE *file;
    long key_sec, key_nsec, *prev_nsec;
    struct timespec spec;
    bool keydown = FALSE;
    char led_cmd[17];
    const char keys[20][2][47] = {
        {"DISPLAY=:0 xte 'keydown Up'\n", "DISPLAY=:0 xte 'keyup Up'\n"},
        {"DISPLAY=:0 xte 'keydown Right'\n", "DISPLAY=:0 xte 'keyup Right'\n"},
        {"DISPLAY=:0 xte 'keydown Down'\n", "DISPLAY=:0 xte 'keyup Down'\n"},
        {"DISPLAY=:0 xte 'keydown Left'\n", "DISPLAY=:0 xte 'keyup Left'\n"},
        {"DISPLAY=:0 xte 'keydown Return'\n", "DISPLAY=:0 xte 'keyup Return'\n"},
        {"DISPLAY=:0 xte 'keydown Escape'\n", "DISPLAY=:0 xte 'keyup Escape'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown M'\n", "DISPLAY=:0 xte 'keyup M' 'keyup Alt_L'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown Tab'\n", "DISPLAY=:0 xte 'keyup Tab' 'keyup Alt_L'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown P'\n", "DISPLAY=:0 xte 'keyup P' 'keyup Alt_L'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown F4'\n", "DISPLAY=:0 xte 'keyup F4' 'keyup Alt_L'\n"},

        {"DISPLAY=:0 xte 'keydown KP_Up'\n", "DISPLAY=:0 xte 'keyup KP_Up'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Right'\n", "DISPLAY=:0 xte 'keyup KP_Right'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Down'\n", "DISPLAY=:0 xte 'keyup KP_Down'\n"},
        {"DISPLAY=:0 xte 'keydown KP_Left'\n", "DISPLAY=:0 xte 'keyup KP_Left'\n"},
        {"DISPLAY=:0 xte 'mouseclick 1'\n", "DISPLAY=:0 xte 'keyup Return'\n"},
        {"DISPLAY=:0 xte 'keydown Escape'\n", "DISPLAY=:0 xte 'keyup Escape'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown M'\n", "DISPLAY=:0 xte 'keyup M' 'keyup Alt_L'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown Tab'\n", "DISPLAY=:0 xte 'keyup Tab' 'keyup Alt_L'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown P'\n", "DISPLAY=:0 xte 'keyup P' 'keyup Alt_L'\n"},
        {"DISPLAY=:0 xte 'keydown Alt_L' 'keydown F4'\n", "DISPLAY=:0 xte 'keyup F4' 'keyup Alt_L'\n"},
    };

    file = fopen("/var/run/keys", "r");

    if (!file) {
        return;
    }

    system("gpio mode 1 out");

    while (TRUE) {
        clock_gettime(CLOCK_REALTIME, &spec);
        fscanf(file, "%i\n", &current_key);
        fscanf(file, "%ld\n", &key_sec);
        fscanf(file, "%ld\n", &key_nsec);

//        printf("QQQQ: %i %ld %ld\n", keydown, spec.tv_nsec, key_nsec);
        if (keydown && ((spec.tv_nsec - key_nsec) >= 213e6 || (spec.tv_sec > key_sec && spec.tv_nsec > 207e6))) {
            if (prev_key == _2NDFX) {
                _2ndfx = abs(_2ndfx - _2NDFX);
                sprintf(led_cmd, "gpio write 1 %i\n", _2ndfx);
                system(led_cmd);
            } else {
//                printf("1: %ld %ld\n", spec.tv_nsec, key_nsec);
                //sprintf(cmd, "DISPLAY=:0 xte 'keyup %s' #1\n", prev_key);
//                printf(&keys[current_key + _2ndfx][1]);
                system(&keys[current_key + _2ndfx][1]);
            }
            prev_nsec = key_nsec;
            keydown = FALSE;
        }

        if (current_key != prev_key || (!keydown && prev_nsec != key_nsec)) {
//            printf("2: %ld %ld\n", prev_nsec, key_nsec);
            //sprintf(cmd, "DISPLAY=:0 xte 'keyup %s' #2\n", prev_key);
//            printf(keys[prev_key + _2ndfx][1]);
            system(keys[prev_key + _2ndfx][1]);
            keydown = TRUE;
            if (current_key != _2NDFX) {
                //sprintf(cmd, "DISPLAY=:0 xte 'keydown %s' #3\n", current_key);
//                printf(&keys[current_key + _2ndfx][0]);
                system(&keys[current_key + _2ndfx][0]);
            }
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

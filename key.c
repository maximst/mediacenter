#include <stdio.h>
#include <time.h>


int main(int argc, char *argv[]) {
    struct timespec spec;
    FILE *file;

    clock_gettime(CLOCK_REALTIME, &spec);

    file = fopen("/var/run/keys", "w+");
    fprintf(file, "%s\n%i.%i", argv[1], (int)spec.tv_sec, (int)spec.tv_nsec);
    fclose(file);
}

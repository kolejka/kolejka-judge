#include <cstdio>
#include <cstring>

int main() {
    char buf[100];
    fgets(buf, 100, stdin);

    if(!strcmp(buf, "Answer is 4")) {
        return 0;
    }
    return 1;
}

#include <iostream>
#include "ver.h"

oi::Scanner in(stdin);

int main() {
    int TT = in.readInt(1, 1e9);
    in.readEoln();
    while (TT--) {
        char buf[256];
        in.readString(buf, sizeof(buf));
        in.readEoln();
    }
    return 0;
}

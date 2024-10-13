#include <array>
#include <iostream>
#include <string>

int stack_consumer(unsigned i, unsigned a) {
    if ( i > 0 ) {
        std::array<unsigned,1024> A;
        for ( unsigned j = 0 ; j < 1024 ; j++ )
            A[j] = i+j;
        A[512] = stack_consumer(i-1, A[512]);
        for ( unsigned j = 0 ; j < 1024 ; j++ )
            A[j] = i-j;
        return A[512];
    }
    return 0;
}

int main() {
    unsigned N;
    std::cin >> N;
    while ( N-- ) {
        std::string s;
        std::cin >> s;
        std::cout << s << std::endl;
        stack_consumer(4096*1024, 0);
    }
    return 0;
}

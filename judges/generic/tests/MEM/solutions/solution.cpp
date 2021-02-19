#include <iostream>
#include <string>

int main() {
    unsigned N;
    std::cin >> N;
    while ( N-- ) {
        std::string s;
        std::cin >> s;
        std::cout << s << std::endl;
        while ( true )
            malloc(4096);
    }
    return 0;
}

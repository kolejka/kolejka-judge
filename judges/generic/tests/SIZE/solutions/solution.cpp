#include <iostream>
#include <string>

int main() {
    unsigned N;
    std::cin >> N;
    while ( N-- ) {
        unsigned M;
        std::cin >> M;
        std::string s;
        std::cin >> s;
        while ( M-- ) {
            std::cout << s << std::endl;
            std::cerr << s << std::endl;
        }
    }
    return 0;
}

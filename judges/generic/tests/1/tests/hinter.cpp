#include <iostream>

int main() {
    int count;
    std::cin >> count;
    for ( int c = 0 ; c < count ; c++ ) {
        std::string test;
        std::cin >> test;
        std::cout << test << std::endl;
    }
    return 0;
}

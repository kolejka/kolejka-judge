#include <chrono>
#include <iostream>
#include <string>
#include <thread>

int main() {
    unsigned N;
    std::cin >> N;
    while ( N-- ) {
        std::string s;
        std::cin >> s;
        std::cout << s << std::endl;
    }
    std::this_thread::sleep_for (std::chrono::seconds(1));
    while ( true ) ;
    return 0;
}

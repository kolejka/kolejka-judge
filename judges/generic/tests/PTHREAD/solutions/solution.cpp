#include <iostream>
#include <string>
#include <thread>

int main() {
    unsigned N;
    std::cin >> N;
    while ( N-- ) {
        std::thread t([]{
            std::string s;
            std::cin >> s;
            std::cout << s << std::endl;
        });
        t.join();
    }
    return 0;
}

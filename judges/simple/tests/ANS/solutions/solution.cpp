#include <algorithm>
#include <iostream>
#include <string>

int main() {
    unsigned N;
    std::cin >> N;
    while ( N-- ) {
        std::string s;
        std::cin >> s;
        std::reverse(s.begin(), s.end());
        std::cout << s << std::endl;
    }
    return 0;
}

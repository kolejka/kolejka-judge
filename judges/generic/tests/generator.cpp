#include <iostream>
#include <random>


int main() {
    int seed;
    int count;
    std::cin >> seed;
    std::cin >> count;

    std::default_random_engine engine(seed);
    using uidc = std::uniform_int_distribution<char>;

    std::cout << count << std::endl;
    for ( int c = 0 ; c < count ; c++ ) {
        for ( int l = 0 ; l < 16 ; l++ )
            std::cout << char('a' + uidc(0,25)(engine));
        std::cout << std::endl;
    }
    return 0;
}

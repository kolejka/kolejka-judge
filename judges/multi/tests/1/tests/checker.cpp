#include <fstream>

int main(int argc, char **argv) {
    std::ifstream input(argv[1]);
    std::ifstream hint(argv[2]);
    std::ifstream answer(argv[3]);
    int count;
    input >> count;
    for ( int c = 0 ; c < count ; c++ ) {
        std::string test;
        std::string test_hint;
        std::string test_answer;
        input >> test;
        hint >> test_hint;
        answer >> test_answer;
        if ( test_hint != test_answer )
            return 1;
    }
    return 0;
}

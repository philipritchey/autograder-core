#include <iostream>
#include "code.h"

// example memory error test
// this is not a good example
// a good memory error test will try to get the code under test to
// violate memory safety, e.g. by attempting access out of bounds

int main() {
    unsigned cnt = 0;
    for (unsigned i = 0; i < 1000; i++) {
        if (is_prime(i)) cnt++;
    }
    std::cout << "found " << cnt << " primes" << std::endl;
    return 0;
}
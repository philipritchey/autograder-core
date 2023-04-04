#include <iostream>
#include "code.h"

int main() {
    unsigned cnt = 0;
    for (unsigned i = 0; i < 1000; i++) {
        if (is_prime(i)) cnt++;
    }
    std::cout << "found " << cnt << " primes" << std::endl;
    return 0;
}
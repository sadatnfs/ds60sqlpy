#include "math.hpp"
#include <iostream>
int main() {
    if (add(2, 3) != 5 || subtract(5, 3) != 2) return 1;
    std::cout << "add=5 subtract=2\n";
    return 0;
}

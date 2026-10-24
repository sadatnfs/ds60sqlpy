#include <iostream>

int twice(int x)  {
     return x*2;
}
int main() {
    if(twice(3)!=6) return 1;
    std::cout << "always-active check passed\n";
    std::cout << "cpp-013 example 1 checks passed\n";
    return 0;
}

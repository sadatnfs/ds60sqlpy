#include <cassert>
#include <future>
#include <iostream>
#include <stdexcept>

int checked_square(int x) {
    if(x<0)throw std::invalid_argument("negative task");
    return x*x;
}
int main() {
    auto f=std::async(std::launch::async,checked_square,3); assert(f.get()==9);
    std::cout << "cpp-032 example 1 checks passed\n";
    return 0;
}

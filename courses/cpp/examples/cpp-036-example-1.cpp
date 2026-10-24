#include <cassert>
#include <iostream>

constexpr int square(int x) {
    return x*x;
}
consteval int fixed_limit() {
    return 16;
}
int main() {
    static_assert(square(4)==16);
    std::cout << "cpp-036 example 1 checks passed\n";
    return 0;
}

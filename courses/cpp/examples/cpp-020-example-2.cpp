#include <cassert>
#include <concepts>
#include <iostream>

#include <concepts>
template<std::integral T> T identity_sum(T a,T b)  {
     return a+b;
}
int main() {
    static_assert(!std::integral<double>);
    std::cout << "cpp-020 example 2 checks passed\n";
    return 0;
}

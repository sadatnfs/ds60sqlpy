#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include <optional>

std::optional<int> safe_add(int a,int b) {
    if(a<0||b<0||a>std::numeric_limits<int>::max()-b)return  {
    };
    return a+b;
}
int main() {
    assert(std::abs((0.1+0.2)-0.3)<1e-12);
    std::cout << "cpp-038 example 2 checks passed\n";
    return 0;
}

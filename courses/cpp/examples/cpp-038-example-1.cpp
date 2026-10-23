#include <cassert>
#include <iostream>
#include <limits>
#include <optional>

std::optional<int> safe_add(int a,int b) {
    if(a<0||b<0||a>std::numeric_limits<int>::max()-b)return  {
    };
    return a+b;
}
int main() {
    assert(!safe_add(std::numeric_limits<int>::max(),1));
    std::cout << "cpp-038 example 1 checks passed\n";
    return 0;
}

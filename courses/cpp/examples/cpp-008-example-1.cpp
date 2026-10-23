#include <cassert>
#include <iostream>
#include <vector>

std::vector<int> doubled(const std::vector<int>& xs)  {
     auto out=xs;
     for(int& x:out) x*=2;
     return out;
}
int main() {
    auto out=doubled(std::vector<int>{2,4});
    assert((out==std::vector<int>{4,8}));
    std::cout << "cpp-008 example 1 checks passed\n";
    return 0;
}

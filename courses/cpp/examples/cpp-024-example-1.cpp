#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>

std::vector<int> reversed(std::vector<int> xs) {
    std::reverse(xs.begin(),xs.end());
    return xs;
}
int main() {
    assert((reversed({1,2,3})==std::vector<int>{3,2,1}));
    std::cout << "cpp-024 example 1 checks passed\n";
    return 0;
}

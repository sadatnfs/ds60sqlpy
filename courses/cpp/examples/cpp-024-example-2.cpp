#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>

std::vector<int> reversed(std::vector<int> xs) {
    std::reverse(xs.begin(),xs.end());
    return xs;
}
int main() {
    assert(reversed(reversed(std::vector<int>{-1,2}))==std::vector<int>({-1,2}));
    std::cout << "cpp-024 example 2 checks passed\n";
    return 0;
}

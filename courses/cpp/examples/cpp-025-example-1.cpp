#include <cassert>
#include <cstddef>
#include <iostream>
#include <vector>

int checked_at(const std::vector<int>& xs,std::size_t i) {
    return xs.at(i);
}
int main() {
    assert(checked_at({2,4},1)==4);
    std::cout << "cpp-025 example 1 checks passed\n";
    return 0;
}

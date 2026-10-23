#include <cassert>
#include <iostream>
#include <numeric>
#include <vector>

int total(const std::vector<int>& xs) {
    return std::accumulate(xs.begin(),xs.end(),0);
}
int main() {
    assert(total({2,4,6})==12);
    std::cout << "cpp-026 example 1 checks passed\n";
    return 0;
}

#include <cassert>
#include <iostream>
#include <numeric>
#include <span>
#include <vector>

long long serial_total(std::span<const int> xs) {
    return std::accumulate(xs.begin(),xs.end(),0LL);
}
int main() {
    const std::vector<int> rows{1,2,3,4,5,6}; assert(serial_total(rows)==21);
    std::cout << "cpp-042 example 1 checks passed\n";
    return 0;
}

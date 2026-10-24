#include <cassert>
#include <iostream>
#include <numeric>
#include <span>
#include <vector>

int sum_view(std::span<const int> xs)  {
     return std::accumulate(xs.begin(),xs.end(),0);
}
int main() {
    std::vector<int> xs{2,4,6}; assert(sum_view(std::span<const int>(xs).subspan(1,2))==10);
    std::cout << "cpp-018 example 1 checks passed\n";
    return 0;
}

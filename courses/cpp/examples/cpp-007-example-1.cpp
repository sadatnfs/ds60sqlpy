#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <vector>


int main() {
    std::vector<int> original{3,1,3,0};
    auto sorted=original;
    std::sort(sorted.begin(),sorted.end());
    assert((sorted==std::vector<int>{0,1,3,3}));
    assert((original==std::vector<int>{3,1,3,0}));
    std::cout << "sorted:";
    for (int value:sorted) std::cout << " " << value;
    std::cout << "\nsum=" << std::accumulate(sorted.begin(),sorted.end(),0LL) << "\n";
    std::cout << "cpp-007 example 1 checks passed\n";
    return 0;
}

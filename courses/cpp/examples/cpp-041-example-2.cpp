#include <iostream>
#include <numeric>
#include <vector>

constexpr int release_schema=1;
int main() {
    std::vector<int> fixture{1,2,3};
    const int total=std::accumulate(fixture.begin(),fixture.end(),0);
    if(total!=6) return 1;
    std::cout << "schema=1 rows=" << fixture.size() << " total=" << total << "\n";
    std::cout << "cpp-041 example 2 checks passed\n";
    return 0;
}

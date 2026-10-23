#include <iostream>
#include <numeric>
#include <vector>

constexpr int release_schema=1;
int main() {
    std::vector<int> fixture{1,2,3};
    if(std::accumulate(fixture.begin(),fixture.end(),0)!=6) return 1;
    std::cout << "cpp-041 example 1 checks passed\n";
    return 0;
}

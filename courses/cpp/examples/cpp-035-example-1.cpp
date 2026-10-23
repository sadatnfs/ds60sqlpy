#include <cassert>
#include <iostream>
#include <map>
#include <vector>


int main() {
    std::map<int,int> counts;
    for(int x:std::vector<int>{2,3,2,4}) ++counts[x];
    assert(counts.at(2)==2 && counts.size()==3);
    std::cout << "cpp-035 example 1 checks passed\n";
    return 0;
}

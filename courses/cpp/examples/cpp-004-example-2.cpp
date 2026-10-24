#include <cassert>
#include <iostream>
#include <vector>

int nonnegative_sum(const std::vector<int>& xs)  {
     int total=0;
     for(int x:xs)  {
         if(x>=0) total+=x;
    } return total;
}
int main() {
    assert(nonnegative_sum({})==0);
    std::cout << "cpp-004 example 2 checks passed\n";
    return 0;
}

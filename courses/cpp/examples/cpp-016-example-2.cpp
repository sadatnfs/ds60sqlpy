#include <cassert>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

struct Batch  {
     std::vector<int> values;
     std::string label;
};
int main() {
    Batch a{{1,2},"A"};
    Batch b=std::move(a);
    assert((b.values==std::vector<int>{1,2}));
    a=Batch{{4},"new"};
    assert(a.values[0]==4);
    std::cout << "cpp-016 example 2 checks passed\n";
    return 0;
}

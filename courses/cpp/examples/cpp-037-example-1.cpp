#include <cassert>
#include <iostream>
#include <ranges>
#include <vector>

template<std::ranges::input_range R> std::vector<int> keep_positive(R&& xs) {
    std::vector<int> out;
    for(auto x:xs)if(x>0)out.push_back(x);
    return out;
}
int main() {
    auto out=keep_positive(std::vector<int>{-1,0,2,2});
    assert((out==std::vector<int>{2,2}));
    std::cout << "cpp-037 example 1 checks passed\n";
    return 0;
}

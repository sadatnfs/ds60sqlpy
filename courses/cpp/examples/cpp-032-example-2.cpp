#include <cassert>
#include <future>
#include <iostream>
#include <stdexcept>

int checked_square(int x) {
    if(x<0)throw std::invalid_argument("negative task");
    return x*x;
}
int main() {
    auto result=std::async(std::launch::async,checked_square,-1);
    bool rejected=false;
    try { (void)result.get(); }
    catch(const std::invalid_argument&) { rejected=true; }
    assert(rejected);
    std::cout << "cpp-032 example 2 checks passed\n";
    return 0;
}

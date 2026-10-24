#include <algorithm>
#include <cassert>
#include <iostream>
#include <stdexcept>

int clamp_reading(int x,int low,int high)  {
     if(low>high) throw std::invalid_argument("reversed bounds");
     return std::max(low,std::min(x,high));
}
int main() {
    bool rejected=false;
    try { (void)clamp_reading(5,10,0); }
    catch (const std::invalid_argument&) { rejected=true; }
    assert(rejected);
    std::cout << "cpp-005 example 2 checks passed\n";
    return 0;
}

#include <cassert>
#include <iostream>
#include <memory>

struct Tracked  {
     int* live;
     explicit Tracked(int& count):live(&count) {
        ++*live;
    } ~Tracked() {
        --*live;
    } Tracked(const Tracked&)=delete;
     Tracked& operator=(const Tracked&)=delete;
};
int main() {
    int live=0;
    { auto owner=std::make_unique<Tracked>(live); assert(live==1); }
    assert(live==0);
    std::cout << "cpp-015 example 2 checks passed\n";
    return 0;
}

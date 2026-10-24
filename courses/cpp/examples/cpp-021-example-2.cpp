#include <cassert>
#include <iostream>

struct Cents  {
     long long value;
     bool operator==(const Cents&)const=default;
};

Cents operator+(Cents a,Cents b) {
    return Cents {
        a.value+b.value
    };
}
int main() {
    assert((Cents{125}+Cents{0})==Cents{125});
    std::cout << "cpp-021 example 2 checks passed\n";
    return 0;
}

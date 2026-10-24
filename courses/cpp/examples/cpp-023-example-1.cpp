#include <cassert>
#include <iostream>
#include <limits>

extern "C" int add_checked(int a,int b,int* out) noexcept  {
     if(!out)return 1;
     if((b>0 && a>std::numeric_limits<int>::max()-b)||(b<0 && a<std::numeric_limits<int>::min()-b))return 2;
     *out=a+b;
    return 0;
}
int main() {
    int out=0; assert(add_checked(2,3,&out)==0 && out==5);
    std::cout << "cpp-023 example 1 checks passed\n";
    return 0;
}

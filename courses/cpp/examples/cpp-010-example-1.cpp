#include <cassert>
#include <iostream>
#include <stdexcept>

enum class Status  {
     pending, paid
};

struct Payment  {
     int id;
     int cents;
     Status status;
};

int settled(const Payment& p)  {
     if(p.cents<0) throw std::invalid_argument("negative cents");
     return p.status==Status::paid?p.cents:0;
}
int main() {
    Payment p{7,200,Status::paid}; assert(settled(p)==200);
    std::cout << "cpp-010 example 1 checks passed\n";
    return 0;
}

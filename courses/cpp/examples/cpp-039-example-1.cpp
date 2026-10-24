#include <cassert>
#include <iostream>
#include <memory>

struct Analyzer  {
     int total=0;
};

extern "C" Analyzer* analyzer_create() noexcept  {
     try {
        return new Analyzer {
        };
    }catch(...) {
        return nullptr;
    }
}
extern "C" void analyzer_destroy(Analyzer* p) noexcept  {
     delete p;
}
extern "C" int analyzer_read(const Analyzer* p,int* out) noexcept  {
    if(!p||!out)return 1;
    *out=p->total;
    return 0;
}
int main() {
    Analyzer* raw=analyzer_create();
    if(!raw) return 1;
    std::unique_ptr<Analyzer,void(*)(Analyzer*)> owner(raw,analyzer_destroy);
    int value=-1;
    assert(analyzer_read(owner.get(),&value)==0 && value==0);
    std::cout << "cpp-039 example 1 checks passed\n";
    return 0;
}

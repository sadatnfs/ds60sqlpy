#include <cassert>
#include <iostream>
#include <numeric>
#include <span>
#include <thread>
#include <vector>

long long serial_total(std::span<const int> xs) {
    return std::accumulate(xs.begin(),xs.end(),0LL);
}
int main() {
    const std::vector<int> rows{1,2,3,4,5,6};long long first=0,second=0;
    std::thread a([&]{first=serial_total(std::span<const int>(rows).first(3));});std::thread b([&]{second=serial_total(std::span<const int>(rows).subspan(3));});a.join();b.join();assert(first==6 && second==15 && first+second==serial_total(rows));
    assert(serial_total(std::span<const int>{})==0);
    std::cout << "cpp-042 example 2 checks passed\n";
    return 0;
}

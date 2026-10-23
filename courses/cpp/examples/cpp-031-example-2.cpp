#include <atomic>
#include <cassert>
#include <iostream>
#include <thread>


int main() {
    int payload=0;
    std::atomic<bool> ready{false};
    std::thread producer([&]{payload=7; ready.store(true,std::memory_order_release);});
    while(!ready.load(std::memory_order_acquire)) std::this_thread::yield();
    assert(payload==7);
    producer.join();
    std::cout << "cpp-031 example 2 checks passed\n";
    return 0;
}

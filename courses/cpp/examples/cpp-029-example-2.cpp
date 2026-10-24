#include <atomic>
#include <cassert>
#include <future>
#include <iostream>
#include <thread>


int main() {
    std::atomic<bool> stop{false};
    std::promise<void> ready;
    auto started=ready.get_future();
    std::thread worker([&]{
        ready.set_value();
        while(!stop.load()) std::this_thread::yield();
    });
    started.get();
    stop.store(true);
    worker.join();
    assert(stop.load());
    std::cout << "cpp-029 example 2 checks passed\n";
    return 0;
}

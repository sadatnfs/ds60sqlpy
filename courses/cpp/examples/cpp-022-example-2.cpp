#include <cassert>
#include <filesystem>
#include <iostream>
#include <string>

std::string encode(int id,int cents) {
    return "v1,"+std::to_string(id)+","+std::to_string(cents);
}
int main() {
    auto path=std::filesystem::path("records")/"batch.csv";
    assert(path.filename()=="batch.csv");
    assert(path.parent_path()=="records");
    std::cout << "cpp-022 example 2 checks passed\n";
    return 0;
}

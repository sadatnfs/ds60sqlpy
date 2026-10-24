#include <cassert>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

std::vector<std::string> read_lines(std::istream& input)  {
     std::vector<std::string> out;
     std::string line;
     while(std::getline(input,line)) out.push_back(line);
     if(input.bad()) throw std::runtime_error("read failed");
     return out;
}
int main() {
    std::istringstream input("10\n20\n");
    auto lines=read_lines(input);
    assert(lines.size()==2);
    std::cout << "cpp-011 example 1 checks passed\n";
    return 0;
}

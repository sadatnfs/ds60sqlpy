#include <cassert>
#include <iostream>
#include <string>
#include <variant>

struct ParseError  {
     std::string reason;
};

using Result=std::variant<int,ParseError>;

Result positive(int x)  {
     if(x<0)return ParseError {
        "negative"
    };
     return x;
}
int main() {
    auto result=positive(0); assert(std::holds_alternative<int>(result));
    std::cout << "cpp-017 example 1 checks passed\n";
    return 0;
}

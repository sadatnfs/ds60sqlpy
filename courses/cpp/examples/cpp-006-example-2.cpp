#include <cassert>
#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

std::optional<int> parse_int(std::string_view s)  {
     int out=0;
     auto [ptr,ec]=std::from_chars(s.data(),s.data()+s.size(),out);
     if(ec!=std::errc {
    } || ptr!=s.data()+s.size()) return std::nullopt;
     return out;
}
int main() {
    assert(!parse_int("12x"));
    std::cout << "cpp-006 example 2 checks passed\n";
    return 0;
}

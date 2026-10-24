#include <cassert>
#include <iostream>
#include <string>
#include <string_view>

bool safe_id(std::string_view s) {
  if (s.empty() || s.size() > 16)
    return false;
  for (unsigned char c : s)
    if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_'))
      return false;
  return true;
}
int main() {
  assert(!safe_id("../secret"));
  std::cout << "cpp-040 example 2 checks passed\n";
  return 0;
}

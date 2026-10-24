#include <cassert>
#include <iostream>

struct Cents {
  long long value;
  bool operator==(const Cents &) const = default;
};

Cents operator+(Cents a, Cents b) { return Cents{a.value + b.value}; }
int main() {
  Cents price{125};
  Cents discount{25};
  assert((discount + Cents{100}) == price);
  std::cout << "cpp-021 example 1 checks passed\n";
  return 0;
}

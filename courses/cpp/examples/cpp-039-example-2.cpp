#include <cassert>
#include <iostream>

struct Analyzer {
  int total = 0;
};

extern "C" Analyzer *analyzer_create() noexcept {
  try {
    return new Analyzer{};
  } catch (...) {
    return nullptr;
  }
}
extern "C" void analyzer_destroy(Analyzer *p) noexcept { delete p; }
extern "C" int analyzer_read(const Analyzer *p, int *out) noexcept {
  if (!p || !out)
    return 1;
  *out = p->total;
  return 0;
}
int main() {
  int out = -1;
  assert(analyzer_read(nullptr, &out) == 1);
  assert(out == -1);
  std::cout << "cpp-039 example 2 checks passed\n";
  return 0;
}

// SPDX-License-Identifier: MIT
#include "ds60_tmbad/models_extra.hpp"
#include <iomanip>
#include <iostream>
using namespace ds60_tmbad;
int main() {
  try {
    std::cout << std::setprecision(17);
    Vector arguments;
    for (int i = 0; i <= 120; ++i)
      arguments.push_back(std::exp(-4.0 + 10.0 * i / 120.0));
    for (double x :
         {.999999999, 1., 1.000000001, 15.999999999, 16., 16.000000001, 64.,
          65., 128., 1000., 10064., 1000000., 1000404.})
      arguments.push_back(x);
    for (double x : arguments) {
      auto function =
          record_function([](const ADVector &p,
                             const Data &) { return log_gamma_positive(p[0]); },
                          {}, {x});
      const auto value = function(Vector{x})[0],
                 gradient = function.Jacobian(Vector{x})[0];
      auto derivative = function.JacFun();
      const auto second = derivative.Jacobian(Vector{x})[0];
      finite_result(value);
      finite_result(gradient);
      finite_result(second);
      const double oracle = std::lgamma(x);
      require(std::abs(value - oracle) <= 3e-14 * (1 + std::abs(oracle)),
              "Independent stdlib log-gamma value mismatch");
      std::cout << "{\"x\":" << x << ",\"value\":" << value
                << ",\"gradient\":" << gradient << ",\"hessian\":" << second
                << "}\n";
    }
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}

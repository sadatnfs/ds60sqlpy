// SPDX-License-Identifier: MIT
#include "gaussian_checks.hpp"
#include <cassert>
#include <memory>
#define Rcout std::cout
#define Rcerr std::cerr
#define TMBAD_ASSERT(x) assert(x)
#define TMBAD_ASSERT2(x, msg) assert(x)
#include <TMBad/TMBad.cpp>
#include <TMBad/TMBad.hpp>
int main() {
  return check("TMBad-from-TMB1.9.25", [](const std::vector<double> &theta,
                                          const std::vector<double> &y) {
    TMBad::ADFun<> function(Gaussian{y}, theta);
    auto jacobian = function.JacFun();
    return Result{function(theta)[0], function.Jacobian(theta),
                  jacobian.Jacobian(theta)};
  });
}

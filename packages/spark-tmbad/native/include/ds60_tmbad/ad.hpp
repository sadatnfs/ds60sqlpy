// SPDX-License-Identifier: MIT
#pragma once
#include "types.hpp"
#include <iostream>
#include <memory>
#define Rcout std::cerr
#define Rcerr std::cerr
#define TMBAD_ASSERT(x)                                                        \
  do {                                                                         \
    if (!(x))                                                                  \
      throw ds60_tmbad::Error("AD_INVARIANT", "AD invariant failed");          \
  } while (false)
#define TMBAD_ASSERT2(x, message) TMBAD_ASSERT(x)
#include <TMBad/TMBad.hpp>

namespace ds60_tmbad {
using AD = TMBad::ad_aug;
using ADVector = std::vector<AD>;
using Function = TMBad::ADFun<>;
using Objective = std::function<AD(const ADVector &, const Data &)>;
struct Model {
  Descriptor descriptor;
  Objective objective;
  std::function<void(const Vector &, const Data &)> validate;
  std::function<Prediction(const Vector &, const Rows &, const Rows &,
                           const std::string &, bool)>
      prediction;
};

inline void check_tape(const Function &function) {
  require(function.glob.values.size() <= 2'000'000,
          "AD tape exceeded its bounded capacity", "RESOURCE_LIMIT");
}
inline Function record_function(const Objective &objective, const Data &data,
                                const Vector &initial) {
  Function result;
  ADVector inputs(initial.size());
  for (std::size_t i = 0; i < initial.size(); ++i)
    inputs[i] = initial[i];
  auto *previous = TMBad::get_glob();
  result.glob.ad_start();
  try {
    TMBad::Independent(inputs);
    ADVector outputs{objective(inputs, data)};
    TMBad::Dependent(outputs);
    result.glob.ad_stop();
  } catch (...) {
    // The Function remains alive while recording context is restored. A failed
    // request still terminates the worker; this is not a recovery/reuse promise.
    result.glob.ad_stop();
    throw;
  }
  require(TMBad::get_glob() == previous, "Recording context was not restored",
          "AD_INVARIANT");
  check_tape(result);
  return result;
}
inline void finite_result(double value) {
  require(std::isfinite(value), "Objective or derivative is nonfinite",
          "NONFINITE_EVALUATION");
}
inline void finite_result(const Vector &values) {
  for (double value : values)
    finite_result(value);
}
} // namespace ds60_tmbad

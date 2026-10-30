// SPDX-License-Identifier: MIT
#pragma once
#include <cmath>
#include <cstddef>
#include <functional>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace ds60_tmbad {
using Vector = std::vector<double>;
using Rows = std::vector<Vector>;
constexpr std::size_t max_rows = 8192;
constexpr std::size_t max_unit_rows = 256;
constexpr std::size_t max_parameters = 64;
constexpr std::size_t max_fields = 256;
constexpr double log_two_pi = 1.83787706640934548356;

struct Error : std::runtime_error {
  std::string code;
  Error(std::string category, const std::string &message)
      : std::runtime_error(message), code(std::move(category)) {}
};
inline void require(bool condition, const char *message,
                    const char *code = "INVALID_INPUT") {
  if (!condition)
    throw Error(code, message);
}
inline void finite(double value,
                   const char *message = "Nonfinite numeric input") {
  require(std::isfinite(value), message);
}
struct Target {
  std::string name;
  std::vector<std::string> fields, columns;
  bool needs_history = false;
  std::string conditioning, uncertainty;
};
struct Descriptor {
  std::string id, version = "1", fit_kind = "rows";
  std::vector<std::string> fit_fields, parameter_names;
  std::vector<std::pair<double, double>> parameter_bounds;
  std::string marginalization = "none";
  std::size_t random_dimension = 0;
  bool ordered = false;
  std::size_t unit_limit = max_unit_rows;
  std::vector<int> derivative_orders{1, 2};
  std::vector<Target> predict, forecast;
};
struct Data {
  Rows rows;
  Vector weights;
};
struct ModeDiagnostics {
  bool used = false;
  std::size_t iterations = 0, line_search_steps = 0, damping_steps = 0,
              roundoff_corrections = 0;
  double score_inf = 0, minimum_eigenvalue = 0, maximum_eigenvalue = 0;
  Vector mode;
};
struct Evaluation {
  double loss = 0;
  Vector gradient, hessian;
  std::size_t row_count = 0, unit_count = 0;
  double weight_sum = 0;
  ModeDiagnostics diagnostics;
};
struct Prediction {
  Rows values;
};
inline void validate_matrix(const Rows &rows, std::size_t width,
                            std::size_t limit) {
  require(rows.size() <= limit, "Row count exceeds the declared limit");
  for (const auto &row : rows) {
    require(row.size() == width, "Numeric row has the wrong field count");
    for (double value : row)
      finite(value);
  }
}
inline double infinity_norm(const Vector &values) {
  double result = 0;
  for (double value : values)
    result = std::max(result, std::abs(value));
  return result;
}
struct Sum {
  double value = 0, correction = 0;
  void add(double item) {
    const double next = value + item;
    correction += std::abs(value) >= std::abs(item) ? (value - next) + item
                                                    : (item - next) + value;
    value = next;
  }
  double total() const { return value + correction; }
};
} // namespace ds60_tmbad

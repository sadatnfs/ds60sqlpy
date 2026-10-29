// SPDX-License-Identifier: MIT
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>
struct Gaussian {
  std::vector<double> y;
  template <class T> std::vector<T> operator()(const std::vector<T> &p) const {
    using std::exp;
    T scale = exp(p[1]);
    T total = 0;
    for (double observation : y) {
      T residual = (T(observation) - p[0]) / scale;
      total += p[1] + T(0.5) * residual * residual + T(0.91893853320467274178);
    }
    return {total};
  }
};
struct Result {
  double value;
  std::vector<double> gradient, hessian;
};
inline Result oracle(const std::vector<double> &p,
                     const std::vector<double> &y) {
  double inverse_variance = std::exp(-2 * p[1]), sum = 0, squared = 0;
  for (double observation : y) {
    sum += p[0] - observation;
    squared += (p[0] - observation) * (p[0] - observation);
  }
  double n = double(y.size());
  return {n * (p[1] + 0.5 * std::log(2 * std::acos(-1.0))) +
              0.5 * squared * inverse_variance,
          {sum * inverse_variance, n - squared * inverse_variance},
          {n * inverse_variance, -2 * sum * inverse_variance,
           -2 * sum * inverse_variance, 2 * squared * inverse_variance}};
}
template <class Evaluator> int check(const char *engine, Evaluator evaluate) {
  double maximum = 0;
  size_t cases = 0;
  for (const std::vector<double> &y :
       std::vector<std::vector<double>>{{1, 2, 4, 7}, {-2, 0, 3, 8}}) {
    for (const std::vector<double> &theta : std::vector<std::vector<double>>{
             {2.2, .3}, {3.5, std::log(std::sqrt(5.25))}, {-3, -.2}}) {
      Result actual = evaluate(theta, y), expected = oracle(theta, y);
      std::vector<double> a{actual.value}, b{expected.value};
      a.insert(a.end(), actual.gradient.begin(), actual.gradient.end());
      a.insert(a.end(), actual.hessian.begin(), actual.hessian.end());
      b.insert(b.end(), expected.gradient.begin(), expected.gradient.end());
      b.insert(b.end(), expected.hessian.begin(), expected.hessian.end());
      if (a.size() != 7 || b.size() != 7)
        throw std::runtime_error("wrong derivative dimensions");
      for (size_t i = 0; i < a.size(); ++i) {
        if (!std::isfinite(a[i]) ||
            std::abs(a[i] - b[i]) > 1e-10 * (1 + std::abs(b[i])))
          throw std::runtime_error("independent Gaussian oracle failed");
        maximum = std::max(maximum, std::abs(a[i] - b[i]));
      }
      ++cases;
    }
  }
  std::cout << std::setprecision(17) << "{\"engine\":\"" << engine
            << "\",\"passed\":true,\"cases\":" << cases
            << ",\"max_value_gradient_hessian_error\":" << maximum << "}\n";
  return 0;
}

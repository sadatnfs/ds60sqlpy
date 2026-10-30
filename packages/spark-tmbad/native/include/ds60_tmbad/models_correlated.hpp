// SPDX-License-Identifier: MIT
#pragma once
#include "models_extra.hpp"

namespace ds60_tmbad {
// QR of the augmented whitened design [I; Z L / sigma]. Positive residual
// squares retain the prior information without forming a rounded Gram matrix.
template <typename Number> struct SlopeQR {
  Number r00 = 1, r01 = 0, r11 = 1, z0 = 0, z1 = 0, residual_square = 0;
  void add(Number a, Number b, Number y) {
    using std::sqrt;
    const Number norm0 = sqrt(r00 * r00 + a * a);
    const Number c0 = r00 / norm0, s0 = a / norm0;
    const Number next01 = c0 * r01 + s0 * b;
    const Number lower = -s0 * r01 + c0 * b;
    const Number next_z0 = c0 * z0 + s0 * y;
    const Number lower_y = -s0 * z0 + c0 * y;
    const Number norm1 = sqrt(r11 * r11 + lower * lower);
    const Number c1 = r11 / norm1, s1 = lower / norm1;
    const Number next_z1 = c1 * z1 + s1 * lower_y;
    const Number remaining = -s1 * z1 + c1 * lower_y;
    residual_square += remaining * remaining;
    r00 = norm0;
    r01 = next01;
    r11 = norm1;
    z0 = next_z0;
    z1 = next_z1;
  }
};
inline Model correlated_gaussian_slope_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "gaussian_correlated_random_slope";
  d.fit_kind = "unit";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"beta0",    "beta1",    "log_sigma",
                       "log_tau0", "log_tau1", "atanh_correlation"};
  d.parameter_bounds = {unbounded(), unbounded(), {-12, 12},
                        {-8, 8},     {-8, 8},     {-4, 4}};
  d.random_dimension = 2;
  d.marginalization = "exact";
  d.predict = {target("existing_group", {"x"}, true,
                      "complete observed group and supplied future x",
                      "exact Gaussian latent posterior plus observation "
                      "variance; no parameter uncertainty"),
               target("new_group", {"x"}, false,
                      "one unseen group and supplied future x",
                      "correlated intercept/slope prior plus observation "
                      "variance; future rows correlated")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows)
      regression_x(row[0]);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    using std::log;
    using std::sqrt;
    using std::tanh;
    const AD tau0 = exp(p[3]), tau1 = exp(p[4]), rho = tanh(p[5]);
    const AD transverse = tau1 * sqrt(1 - rho * rho), sigma = exp(p[2]);
    SlopeQR<AD> factor;
    for (const auto &row : data.rows) {
      const AD r0 = tau0 + row[0] * rho * tau1, r1 = row[0] * transverse;
      const AD residual = row[1] - p[0] - p[1] * row[0];
      factor.add(r0 / sigma, r1 / sigma, residual / sigma);
    }
    const double n = static_cast<double>(data.rows.size());
    return .5 * (n * log_two_pi + 2 * n * p[2] + 2 * log(factor.r00) +
                 2 * log(factor.r11) + factor.residual_square);
  };
  model.prediction = [](const Vector &p, const Rows &future,
                        const Rows &history, const std::string &name, bool) {
    const double sigma2 = std::exp(2 * p[2]), tau0 = std::exp(p[3]);
    const double tau1 = std::exp(p[4]), rho = std::tanh(p[5]);
    const double transverse = tau1 * std::sqrt(1 - rho * rho);
    const double sigma = std::exp(p[2]);
    SlopeQR<double> factor;
    if (name == "existing_group") {
      require(!history.empty(), "Existing group needs complete history");
      for (const auto &row : history) {
        regression_x(row[0]);
        const double r0 = tau0 + row[0] * rho * tau1, r1 = row[0] * transverse;
        factor.add(r0 / sigma, r1 / sigma,
                   (row[1] - p[0] - p[1] * row[0]) / sigma);
      }
    } else {
      require(history.empty(),
              "New group must not supply conditioning history");
    }
    const double u1 = factor.z1 / factor.r11;
    const double u0 = (factor.z0 - factor.r01 * u1) / factor.r00;
    finite_result(u0);
    finite_result(u1);
    Prediction result;
    for (const auto &row : future) {
      regression_x(row[0]);
      const double r0 = tau0 + row[0] * rho * tau1, r1 = row[0] * transverse;
      const double v0 = r0 / factor.r00;
      const double v1 = (r1 - factor.r01 * v0) / factor.r11;
      result.values.push_back(moments(p[0] + p[1] * row[0] + r0 * u0 + r1 * u1,
                                      sigma2 + v0 * v0 + v1 * v1));
    }
    return result;
  };
  return model;
}

} // namespace ds60_tmbad

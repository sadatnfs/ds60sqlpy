// SPDX-License-Identifier: MIT
#pragma once
// Original build-time extension example. Add reviewed models here and rebuild
// the prepared artifact; runtime requests never contain source or compiler flags.
#include "ds60_tmbad/models.hpp"
namespace ds60_tmbad {
inline Model saturating_growth_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "saturating_growth";
  d.fit_fields = {"time", "y"};
  d.parameter_names = {"baseline", "log_amplitude", "log_rate", "log_sigma"};
  d.parameter_bounds = {unbounded(), {-12, 12}, {-12, 5}, {-20, 20}};
  d.predict = {target("response", {"time"}, false,
                      "supplied nonnegative time and fitted growth parameters",
                      "independent Gaussian observation variance around the "
                      "growth curve; no parameter uncertainty")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows)
      require(row[0] >= 0 && row[0] <= 1e6,
              "Growth time must be in [0, 1000000]", "DOMAIN_ERROR");
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    using std::expm1;
    AD value = 0;
    const AD amplitude = exp(p[1]), rate = exp(p[2]), inverse = exp(-2 * p[3]);
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const AD mean = p[0] - amplitude * expm1(-rate * data.rows[i][0]);
      const AD residual = data.rows[i][1] - mean;
      value += data.weights[i] *
               (p[3] + .5 * log_two_pi + .5 * residual * residual * inverse);
    }
    return value;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    for (const auto &row : rows) {
      require(row[0] >= 0 && row[0] <= 1e6,
              "Growth time must be in [0, 1000000]", "DOMAIN_ERROR");
      result.values.push_back(
          moments(p[0] - std::exp(p[1]) * std::expm1(-std::exp(p[2]) * row[0]),
                  std::exp(2 * p[3])));
    }
    return result;
  };
  return model;
}
inline std::vector<Model> custom_models() {
  Model model;
  auto &d = model.descriptor;
  d.id = "quadratic_gaussian";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"intercept", "curvature", "log_sigma"};
  d.parameter_bounds = {unbounded(), unbounded(), {-20, 20}};
  d.predict = {target(
      "response", {"x"}, false, "supplied squared design and fitted parameters",
      "Gaussian observation variance; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows)
      require(std::abs(row[0]) <= 1e6,
              "Quadratic design exceeds its numeric domain", "DOMAIN_ERROR");
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const double x = data.rows[i][0];
      const AD residual = data.rows[i][1] - p[0] - p[1] * (x * x);
      total += data.weights[i] * (p[2] + 0.5 * log_two_pi +
                                  0.5 * residual * residual * exp(-2 * p[2]));
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    for (const auto &row : rows) {
      require(std::abs(row[0]) <= 1e6,
              "Quadratic prediction exceeds its numeric domain",
              "DOMAIN_ERROR");
      result.values.push_back(
          moments(p[0] + p[1] * row[0] * row[0], std::exp(2 * p[2])));
    }
    return result;
  };
  return {model, saturating_growth_model()};
}
} // namespace ds60_tmbad

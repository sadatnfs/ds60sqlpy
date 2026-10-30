// SPDX-License-Identifier: MIT
#pragma once
#include "models.hpp"
namespace ds60_tmbad {
inline AD softplus(const AD &x) {
  using std::exp;
  using std::log1p;
  // Each row objective is retaped at its requested parameters. Both expressions
  // are the same smooth function, with the branch choosing a stable evaluation.
  return TMBad::Value(x) > 0 ? x + log1p(exp(-x)) : log1p(exp(x));
}
inline AD log_gamma_positive(AD x) {
  using std::log;
  require(TMBad::Value(x) > 0 && TMBad::Value(x) <= 2e6,
          "Log-gamma argument is outside the qualified positive domain",
          "DOMAIN_ERROR");
  AD correction = 0;
  // Shift to at least16. The finite recurrence is exact; the following bounded
  // eight-term Stirling/Bernoulli expansion is explicitly qualified by oracles.
  while (TMBad::Value(x) < 16) {
    correction -= log(x);
    x += 1;
  }
  const AD inverse = 1 / x, square = inverse * inverse;
  AD series = -3617.0 / 122400.0;
  series = 1.0 / 156.0 + square * series;
  series = -691.0 / 360360.0 + square * series;
  series = 1.0 / 1188.0 + square * series;
  series = -1.0 / 1680.0 + square * series;
  series = 1.0 / 1260.0 + square * series;
  series = -1.0 / 360.0 + square * series;
  series = 1.0 / 12.0 + square * series;
  return correction + (x - .5) * log(x) - x + .5 * log_two_pi +
         inverse * series;
}
inline void regression_x(double x) {
  require(std::abs(x) <= 5, "Regression covariate exceeds its numeric domain",
          "DOMAIN_ERROR");
}
inline Model bernoulli_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "bernoulli_logistic";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"intercept", "slope"};
  d.parameter_bounds = {{-40, 40}, {-40, 40}};
  d.predict = {target("response", {"x"}, false,
                      "supplied covariates and fitted parameters",
                      "Bernoulli observation variance; no parameter "
                      "uncertainty; future rows conditionally independent")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows) {
      regression_x(row[0]);
      require(row[1] == 0 || row[1] == 1,
              "Bernoulli response must be zero or one", "DOMAIN_ERROR");
    }
  };
  model.objective = [](const ADVector &p, const Data &data) {
    AD value = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const AD eta = p[0] + p[1] * data.rows[i][0];
      value += data.weights[i] * softplus(data.rows[i][1] == 1 ? -eta : eta);
    }
    return value;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    for (const auto &row : rows) {
      regression_x(row[0]);
      const double eta = p[0] + p[1] * row[0], e = std::exp(-std::abs(eta));
      const double mean = eta >= 0 ? 1 / (1 + e) : e / (1 + e);
      result.values.push_back(moments(mean, e / ((1 + e) * (1 + e))));
    }
    return result;
  };
  return model;
}
inline Model negative_binomial_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "negative_binomial2";
  d.fit_fields = {"x", "exposure", "y"};
  d.parameter_names = {"intercept", "slope", "log_shape"};
  d.parameter_bounds = {{-12, 12}, {-3, 3}, {-4, 6}};
  d.predict = {target(
      "response", {"x", "exposure"}, false,
      "supplied covariates/exposure and fitted parameters",
      "NB2 observation variance mu+mu^2/shape; no parameter uncertainty")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    validate_counts(data, 1, 2, 0);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    using std::log;
    const AD shape = exp(p[2]);
    AD value = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const double y = row[2];
      const AD log_mu = p[0] + p[1] * row[0] + std::log(row[1]);
      AD gamma_ratio = 0;
      if (y <= 64)
        for (int k = 0; k < static_cast<int>(y); ++k)
          gamma_ratio -= log(shape + k);
      else
        gamma_ratio = log_gamma_positive(shape) - log_gamma_positive(shape + y);
      const AD nll = gamma_ratio + std::lgamma(y + 1) + y * (p[2] - log_mu) +
                     (shape + y) * softplus(log_mu - p[2]);
      value += data.weights[i] * nll;
    }
    return value;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    const double shape = std::exp(p[2]);
    for (const auto &row : rows) {
      regression_x(row[0]);
      require(row[1] > 0 && row[1] <= 1e6,
              "Prediction exposure is outside its domain", "DOMAIN_ERROR");
      const double mean = row[1] * std::exp(p[0] + p[1] * row[0]);
      result.values.push_back(moments(mean, mean + mean * mean / shape));
    }
    return result;
  };
  return model;
}
inline Model gamma_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "gamma_regression";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"intercept", "slope", "log_shape"};
  d.parameter_bounds = {{-12, 12}, {-3, 3}, {-4, 6}};
  d.predict = {target(
      "response", {"x"}, false, "supplied covariates and fitted parameters",
      "Gamma observation variance mu^2/shape; no parameter uncertainty")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows) {
      regression_x(row[0]);
      require(row[1] > 0 && row[1] <= 1e12,
              "Gamma response must be in (0, 1e12]", "DOMAIN_ERROR");
    }
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    const AD shape = exp(p[2]),
             normalization = log_gamma_positive(shape) - shape * p[2];
    AD value = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const AD log_mu = p[0] + p[1] * row[0];
      const double log_y = std::log(row[1]);
      value +=
          data.weights[i] * (normalization + log_y +
                             shape * (log_mu - log_y + row[1] * exp(-log_mu)));
    }
    return value;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    const double shape = std::exp(p[2]);
    for (const auto &row : rows) {
      regression_x(row[0]);
      const double mean = std::exp(p[0] + p[1] * row[0]);
      result.values.push_back(moments(mean, mean * mean / shape));
    }
    return result;
  };
  return model;
}
} // namespace ds60_tmbad

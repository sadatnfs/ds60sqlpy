// SPDX-License-Identifier: MIT
#pragma once
#include "engine.hpp"
#include <algorithm>
#include <map>

namespace ds60_tmbad {
inline std::pair<double, double> unbounded() {
  return {-std::numeric_limits<double>::infinity(),
          std::numeric_limits<double>::infinity()};
}
inline Target
target(std::string name, std::vector<std::string> fields, bool history,
       std::string conditioning, std::string uncertainty,
       std::vector<std::string> columns = std::vector<std::string>{
           "mean", "variance", "sd"}) {
  return {std::move(name), std::move(fields),       std::move(columns),
          history,         std::move(conditioning), std::move(uncertainty)};
}
inline void validate_counts(const Data &data, std::size_t exposure,
                            std::size_t response, std::size_t x = max_fields) {
  for (const auto &row : data.rows) {
    require(row[exposure] > 0 && row[exposure] <= 1e6,
            "Exposure must be in (0, 1000000]", "DOMAIN_ERROR");
    require(row[response] >= 0 && row[response] <= 1e6 &&
                std::floor(row[response]) == row[response],
            "Count response must be an integer in [0, 1000000]",
            "DOMAIN_ERROR");
    if (x != max_fields)
      require(std::abs(row[x]) <= 5,
              "Count-model covariate exceeds its numeric domain",
              "DOMAIN_ERROR");
  }
}
inline void validate_time(const Rows &rows, std::size_t minimum = 1) {
  require(rows.size() >= minimum && rows.size() <= max_unit_rows,
          "Time series needs a bounded nonempty history");
  for (std::size_t i = 0; i < rows.size(); ++i) {
    const double time = rows[i][0];
    require(std::floor(time) == time && std::abs(time) <= 0x1p50,
            "Time must be an exactly supported integer step index");
    if (i)
      require(time - rows[i - 1][0] == 1,
              "Time series must have consecutive unit-spaced indices");
  }
}
inline void validate_future_time(const Rows &future, const Rows &history,
                                 bool existing) {
  validate_time(future);
  if (existing) {
    validate_time(history);
    require(future.front()[0] == history.back()[0] + 1,
            "Future indices must start one step after the complete history");
  } else
    require(history.empty(),
            "New-series forecasts must not supply conditioning history");
}
inline Vector moments(double mean, double variance) {
  finite_result(mean);
  finite_result(variance);
  require(variance >= 0, "Predictive variance is negative", "MODEL_CONTRACT");
  return {mean, variance, std::sqrt(variance)};
}
inline double mean_y(const Rows &rows, std::size_t column) {
  require(!rows.empty(), "History cannot be empty");
  Sum mean;
  for (const auto &row : rows)
    mean.add(row[column] / static_cast<double>(rows.size()));
  finite_result(mean.total());
  return mean.total();
}

inline Model normal_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "normal";
  d.fit_fields = {"y"};
  d.parameter_names = {"mu", "log_sigma"};
  d.parameter_bounds = {unbounded(), {-20, 20}};
  d.predict = {target("response", {}, false, "fitted parameters",
                      "observation only; parameter uncertainty excluded",
                      {"mean", "sd"})};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &) {};
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    AD total = 0;
    const AD inverse = exp(-2 * p[1]);
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const AD error = data.rows[i][0] - p[0];
      total += data.weights[i] *
               (p[1] + 0.5 * log_two_pi + 0.5 * error * error * inverse);
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &future, const Rows &,
                        const std::string &, bool) {
    return Prediction{Rows(future.size(), Vector{p[0], std::exp(p[1])})};
  };
  return model;
}
inline Model linear_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "linear_gaussian";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"beta0", "beta1", "log_sigma"};
  d.parameter_bounds = {unbounded(), unbounded(), {-20, 20}};
  d.predict = {target("response", {"x"}, false,
                      "fitted parameters and supplied x",
                      "observation only; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &) {};
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const AD error = data.rows[i][1] - p[0] - p[1] * data.rows[i][0];
      total += data.weights[i] *
               (p[2] + 0.5 * log_two_pi + 0.5 * error * error * exp(-2 * p[2]));
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &future, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    for (const auto &row : future)
      result.values.push_back(
          moments(p[0] + p[1] * row[0], std::exp(2 * p[2])));
    return result;
  };
  return model;
}
inline Model poisson_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "poisson_exposure";
  d.fit_fields = {"x", "exposure", "y"};
  d.parameter_names = {"intercept", "slope"};
  d.parameter_bounds = {{-10, 10}, {-3, 3}};
  d.predict = {
      target("response", {"x", "exposure"}, false,
             "fitted parameters and supplied exposure",
             "Poisson observation variance; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    validate_counts(data, 1, 2, 0);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const AD eta = p[0] + p[1] * row[0] + std::log(row[1]);
      total +=
          data.weights[i] * (exp(eta) - row[2] * eta + std::lgamma(row[2] + 1));
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &future, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    for (const auto &row : future) {
      require(row[1] > 0 && row[1] <= 1e6 && std::abs(row[0]) <= 5,
              "Prediction exposure/covariate is outside the model domain",
              "DOMAIN_ERROR");
      const double mean = std::exp(p[0] + p[1] * row[0] + std::log(row[1]));
      result.values.push_back(moments(mean, mean));
    }
    return result;
  };
  return model;
}
inline std::pair<double, double>
random_intercept_posterior(const Vector &p, const Rows &history) {
  const double sigma2 = std::exp(2 * p[1]), tau2 = std::exp(2 * p[2]);
  const double n = static_cast<double>(history.size());
  const double variance = sigma2 * tau2 / (sigma2 + n * tau2);
  const double mean =
      n * tau2 * (mean_y(history, 0) - p[0]) / (sigma2 + n * tau2);
  return {mean, variance};
}
inline Model random_intercept_model(bool approximate = false) {
  Model model;
  auto &d = model.descriptor;
  d.id = approximate ? "gaussian_random_intercept_laplace"
                     : "gaussian_random_intercept";
  d.fit_kind = "unit";
  d.fit_fields = {"y"};
  d.parameter_names = {"beta", "log_sigma", "log_tau"};
  d.parameter_bounds = {unbounded(), {-20, 20}, {-20, 20}};
  d.random_dimension = 1;
  d.marginalization = approximate ? "laplace" : "exact";
  if (approximate)
    d.derivative_orders = {1};
  d.predict = {target("existing_group", {}, true,
                      "complete observed group and fitted parameters",
                      "exact posterior latent and future observation variance; "
                      "parameter uncertainty excluded"),
               target("new_group", {}, false,
                      "one new group and fitted parameters",
                      "prior latent and observation variance; shared latent "
                      "induces cross-step dependence")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &) {};
  if (approximate) {
    model.objective = [](const ADVector &p, const Data &data) {
      using std::exp;
      const AD u = p[3];
      AD total = p[2] + 0.5 * log_two_pi + 0.5 * u * u * exp(-2 * p[2]);
      for (const auto &row : data.rows) {
        const AD error = row[0] - p[0] - u;
        total += p[1] + 0.5 * log_two_pi + 0.5 * error * error * exp(-2 * p[1]);
      }
      return total;
    };
  } else {
    model.objective = [](const ADVector &p, const Data &data) {
      using std::exp;
      using std::log;
      const double n = static_cast<double>(data.rows.size());
      const double mean = mean_y(data.rows, 0);
      double centered = 0;
      for (const auto &row : data.rows)
        centered += (row[0] - mean) * (row[0] - mean);
      const AD sigma2 = exp(2 * p[1]), tau2 = exp(2 * p[2]);
      const AD shift = mean - p[0];
      return 0.5 *
             (n * log_two_pi + (n - 1) * 2 * p[1] + log(sigma2 + n * tau2) +
              centered / sigma2 + n * shift * shift / (sigma2 + n * tau2));
    };
  }
  model.prediction = [](const Vector &p, const Rows &future,
                        const Rows &history, const std::string &name, bool) {
    const double sigma2 = std::exp(2 * p[1]), tau2 = std::exp(2 * p[2]);
    double mean = p[0], variance = sigma2 + tau2;
    if (name == "existing_group") {
      const auto posterior = random_intercept_posterior(p, history);
      mean += posterior.first;
      variance = sigma2 + posterior.second;
    }
    return Prediction{Rows(future.size(), moments(mean, variance))};
  };
  return model;
}
inline Model ar1_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "ar1";
  d.fit_kind = "unit";
  d.fit_fields = {"time", "y"};
  d.ordered = true;
  d.parameter_names = {"mu", "atanh_phi", "log_sigma"};
  d.parameter_bounds = {unbounded(), {-7, 7}, {-20, 20}};
  d.predict = {
      target("response", {"lag"}, false,
             "one supplied exact previous observation and fitted parameters",
             "one innovation variance; parameter uncertainty excluded")};
  d.forecast = {
      target("conditional_history", {"time"}, true,
             "last exact observation of complete unit-spaced integer history "
             "and fitted parameters",
             "propagated future innovations; pointwise variance, not "
             "simultaneous intervals"),
      target("stationary_new_series", {"time"}, false,
             "new stationary unit-spaced series and fitted parameters",
             "stationary marginal variance; future steps are correlated")};
  model.validate = [](const Vector &, const Data &data) {
    validate_time(data.rows);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    using std::log;
    using std::tanh;
    const AD phi = tanh(p[1]), sigma2 = exp(2 * p[2]);
    const AD first = data.rows[0][1] - p[0];
    AD total = p[2] - 0.5 * log(1 - phi * phi) + 0.5 * log_two_pi +
               0.5 * (1 - phi * phi) * first * first / sigma2;
    for (std::size_t i = 1; i < data.rows.size(); ++i) {
      const AD error =
          data.rows[i][1] - p[0] - phi * (data.rows[i - 1][1] - p[0]);
      total += p[2] + 0.5 * log_two_pi + 0.5 * error * error / sigma2;
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &future,
                        const Rows &history, const std::string &name,
                        bool forecast) {
    const double phi = std::tanh(p[1]), sigma2 = std::exp(2 * p[2]);
    Prediction result;
    if (!forecast) {
      for (const auto &row : future)
        result.values.push_back(moments(p[0] + phi * (row[0] - p[0]), sigma2));
      return result;
    }
    const bool existing = name == "conditional_history";
    validate_future_time(future, history, existing);
    double power = 1, variance = 0;
    for (std::size_t i = 0; i < future.size(); ++i) {
      power *= phi;
      variance = sigma2 + phi * phi * variance;
      result.values.push_back(
          existing
              ? moments(p[0] + power * (history.back()[1] - p[0]), variance)
              : moments(p[0], sigma2 / (1 - phi * phi)));
    }
    return result;
  };
  return model;
}
inline Model ar1_random_intercept_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "gaussian_ar1_random_intercept";
  d.fit_kind = "unit";
  d.fit_fields = {"time", "y"};
  d.ordered = true;
  d.parameter_names = {"beta", "atanh_phi", "log_sigma", "log_tau"};
  d.parameter_bounds = {unbounded(), {-7, 7}, {-20, 20}, {-20, 20}};
  d.random_dimension = 1;
  d.marginalization = "exact";
  d.forecast = {
      target("conditional_history", {"time"}, true,
             "complete exact Gaussian history of one group with consecutive "
             "integer times and fitted parameters",
             "posterior latent uncertainty and propagated innovations; "
             "pointwise variance excludes parameter uncertainty"),
      target("stationary_new_series", {"time"}, false,
             "one new stationary group and fitted parameters",
             "prior shared latent plus stationary AR1 variance; future steps "
             "are correlated")};
  // This conditional operation may be requested through either explicit surface.
  d.predict = d.forecast;
  model.validate = [](const Vector &, const Data &data) {
    validate_time(data.rows);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    using std::log;
    using std::tanh;
    const std::size_t n = data.rows.size();
    const AD phi = tanh(p[1]), sigma2 = exp(2 * p[2]), tau2 = exp(2 * p[3]);
    const AD one = 1 - phi;
    const AD q1 =
        ((1 - phi * phi) + static_cast<double>(n - 1) * one * one) / sigma2;
    AD cross = (1 - phi * phi) * (data.rows[0][1] - p[0]);
    for (std::size_t i = 1; i < n; ++i)
      cross +=
          one * (data.rows[i][1] - p[0] - phi * (data.rows[i - 1][1] - p[0]));
    cross /= sigma2;
    const AD center = cross / q1;
    const AD first = data.rows[0][1] - p[0] - center;
    AD quadratic = (1 - phi * phi) * first * first;
    for (std::size_t i = 1; i < n; ++i) {
      const AD error = data.rows[i][1] - p[0] - center -
                       phi * (data.rows[i - 1][1] - p[0] - center);
      quadratic += error * error;
    }
    quadratic = quadratic / sigma2 + center * center * q1 / (1 + tau2 * q1);
    const AD logdet = 2 * static_cast<double>(n) * p[2] - log(1 - phi * phi) +
                      log(1 + tau2 * q1);
    return 0.5 * (static_cast<double>(n) * log_two_pi + logdet + quadratic);
  };
  model.prediction = [](const Vector &p, const Rows &future,
                        const Rows &history, const std::string &name, bool) {
    const bool existing = name == "conditional_history";
    validate_future_time(future, history, existing);
    const double phi = std::tanh(p[1]), sigma2 = std::exp(2 * p[2]),
                 tau2 = std::exp(2 * p[3]);
    double latent_mean = 0, latent_variance = tau2;
    if (existing) {
      const double one = 1 - phi;
      const double q1 = ((1 - phi * phi) +
                         static_cast<double>(history.size() - 1) * one * one) /
                        sigma2;
      Sum cross;
      cross.add((1 - phi * phi) * (history[0][1] - p[0]));
      for (std::size_t i = 1; i < history.size(); ++i)
        cross.add(one *
                  (history[i][1] - p[0] - phi * (history[i - 1][1] - p[0])));
      latent_variance = 1 / (1 / tau2 + q1);
      latent_mean = latent_variance * cross.total() / sigma2;
    }
    Prediction result;
    double power = 1, innovation_variance = 0;
    for (std::size_t i = 0; i < future.size(); ++i) {
      power *= phi;
      innovation_variance = sigma2 + phi * phi * innovation_variance;
      result.values.push_back(
          existing ? moments(p[0] + power * (history.back()[1] - p[0]) +
                                 (1 - power) * latent_mean,
                             (1 - power) * (1 - power) * latent_variance +
                                 innovation_variance)
                   : moments(p[0], tau2 + sigma2 / (1 - phi * phi)));
    }
    return result;
  };
  return model;
}
inline Model poisson_random_intercept_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "poisson_random_intercept";
  d.fit_kind = "unit";
  d.fit_fields = {"exposure", "y"};
  d.parameter_names = {"beta", "log_tau"};
  d.parameter_bounds = {{-10, 10}, {-4, 1}};
  d.random_dimension = 1;
  d.marginalization = "laplace";
  d.derivative_orders = {1};
  d.predict = {
      target("existing_group", {"exposure"}, true,
             "local Gaussian Laplace posterior for the observed group and "
             "fitted parameters",
             "Poisson/lognormal moments under Laplace posterior approximation; "
             "no parameter uncertainty"),
      target(
          "new_group", {"exposure"}, false,
          "one new group and fitted parameters",
          "exact prior Poisson/lognormal moments; no parameter uncertainty")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    validate_counts(data, 0, 1);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    const AD u = p[2];
    AD total = p[1] + 0.5 * log_two_pi + 0.5 * u * u * exp(-2 * p[1]);
    for (const auto &row : data.rows) {
      const AD eta = p[0] + u + std::log(row[0]);
      total += exp(eta) - row[1] * eta + std::lgamma(row[1] + 1);
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &future,
                        const Rows &history, const std::string &name, bool) {
    double latent_mean = 0, latent_variance = std::exp(2 * p[1]);
    if (name == "existing_group") {
      auto model = poisson_random_intercept_model();
      Data observed{history, {}};
      model.validate(p, observed);
      auto posterior = laplace(model, p, observed);
      latent_mean = posterior.diagnostics.mode[0];
      latent_variance = posterior.latent_covariance(0, 0);
    }
    Prediction result;
    for (const auto &row : future) {
      require(row[0] > 0 && row[0] <= 1e6,
              "Prediction exposure is outside its domain", "DOMAIN_ERROR");
      const double mean =
          row[0] * std::exp(p[0] + latent_mean + 0.5 * latent_variance);
      result.values.push_back(
          moments(mean, mean + mean * mean * std::expm1(latent_variance)));
    }
    return result;
  };
  return model;
}
inline Model poisson_random_slope_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "poisson_random_slope";
  d.fit_kind = "unit";
  d.fit_fields = {"x", "exposure", "y"};
  d.parameter_names = {"beta0", "beta1", "log_tau0", "log_tau1"};
  d.parameter_bounds = {{-10, 10}, {-3, 3}, {-4, 1}, {-4, 1}};
  d.random_dimension = 2;
  d.marginalization = "laplace";
  d.derivative_orders = {1};
  model.validate = [](const Vector &, const Data &data) {
    validate_counts(data, 1, 2, 0);
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    const AD u0 = p[4], u1 = p[5];
    AD total = p[2] + p[3] + log_two_pi + 0.5 * u0 * u0 * exp(-2 * p[2]) +
               0.5 * u1 * u1 * exp(-2 * p[3]);
    for (const auto &row : data.rows) {
      const AD eta = p[0] + p[1] * row[0] + u0 + u1 * row[0] + std::log(row[1]);
      total += exp(eta) - row[2] * eta + std::lgamma(row[2] + 1);
    }
    return total;
  };
  d.predict = {
      target("existing_group", {"x", "exposure"}, true,
             "local Gaussian Laplace posterior for both observed-group latent "
             "effects and fitted parameters",
             "Poisson/lognormal moments under multivariate Laplace "
             "approximation; no parameter uncertainty"),
      target(
          "new_group", {"x", "exposure"}, false,
          "one new group and fitted parameters at supplied future covariates",
          "exact prior Poisson/lognormal moments; shared latent effects induce "
          "cross-row dependence")};
  d.forecast = d.predict;
  model.prediction = [](const Vector &p, const Rows &future,
                        const Rows &history, const std::string &name, bool) {
    Eigen::Vector2d latent_mean = Eigen::Vector2d::Zero();
    Eigen::Matrix2d latent_covariance = Eigen::Matrix2d::Zero();
    latent_covariance(0, 0) = std::exp(2 * p[2]);
    latent_covariance(1, 1) = std::exp(2 * p[3]);
    if (name == "existing_group") {
      auto prepared = poisson_random_slope_model();
      Data observed{history, {}};
      prepared.validate(p, observed);
      const auto posterior = laplace(prepared, p, observed);
      latent_mean(0) = posterior.diagnostics.mode[0];
      latent_mean(1) = posterior.diagnostics.mode[1];
      latent_covariance = posterior.latent_covariance;
    }
    Prediction result;
    for (const auto &row : future) {
      require(std::abs(row[0]) <= 5 && row[1] > 0 && row[1] <= 1e6,
              "Prediction exposure/covariate is outside the model domain",
              "DOMAIN_ERROR");
      const Eigen::Vector2d design(1, row[0]);
      const double latent_variance = design.dot(latent_covariance * design);
      const double mean =
          row[1] * std::exp(p[0] + p[1] * row[0] + design.dot(latent_mean) +
                            .5 * latent_variance);
      result.values.push_back(
          moments(mean, mean + mean * mean * std::expm1(latent_variance)));
    }
    return result;
  };
  return model;
}

inline const Target &find_target(const Model &model, const std::string &name,
                                 bool forecast) {
  const auto &targets =
      forecast ? model.descriptor.forecast : model.descriptor.predict;
  const auto found =
      std::find_if(targets.begin(), targets.end(),
                   [&](const Target &t) { return t.name == name; });
  require(found != targets.end() && static_cast<bool>(model.prediction),
          "Model does not declare the requested prediction target",
          "UNSUPPORTED_OPERATION");
  return *found;
}
inline Prediction predict(const Model &model, const Vector &theta,
                          const Rows &future, const Rows &history,
                          const std::string &name, bool forecast) {
  validate_parameters(model, theta);
  const auto &spec = find_target(model, name, forecast);
  validate_matrix(future, spec.fields.size(),
                  forecast || model.descriptor.fit_kind == "unit"
                      ? model.descriptor.unit_limit
                      : max_rows);
  if (forecast)
    require(!future.empty(), "Forecast horizon must be nonempty");
  validate_matrix(history, model.descriptor.fit_fields.size(),
                  model.descriptor.unit_limit);
  require(spec.needs_history ? !history.empty() : history.empty(),
          "History presence differs from the declared prediction target");
  if (spec.needs_history)
    model.validate(theta, Data{history, {}});
  auto result = model.prediction(theta, future, history, name, forecast);
  require(result.values.size() == future.size(),
          "Prediction cardinality differs", "MODEL_CONTRACT");
  validate_matrix(result.values, spec.columns.size(), future.size());
  return result;
}
} // namespace ds60_tmbad

// SPDX-License-Identifier: MIT
#pragma once
#include "models_extra.hpp"

namespace ds60_tmbad {
inline double stable_probability(double eta) {
  const double e = std::exp(-std::abs(eta));
  return eta >= 0 ? 1 / (1 + e) : e / (1 + e);
}
inline AD log_add(const AD &left, const AD &right) {
  return TMBad::Value(left) >= TMBad::Value(right)
             ? left + softplus(right - left)
             : right + softplus(left - right);
}
// Stable log Gamma(x+a)-log Gamma(x), preserving small increments at large x.
inline AD log_gamma_increment(AD x, const AD &increment) {
  using std::log;
  using std::log1p;
  require(TMBad::Value(x) > 0 && TMBad::Value(increment) >= 0 &&
              TMBad::Value(x + increment) <= 2e6,
          "Gamma ratio exceeds its qualified positive domain", "DOMAIN_ERROR");
  AD correction = 0;
  while (TMBad::Value(x) < 16) {
    correction -= log1p(increment / x);
    x += 1;
  }
  const AD old_inverse = 1 / x, new_inverse = 1 / (x + increment);
  const AD delta_inverse = -increment / (x * (x + increment));
  const AD old_square = old_inverse * old_inverse,
           new_square = new_inverse * new_inverse;
  const double coefficient[] = {1.0 / 12,    -1.0 / 360,      1.0 / 1260,
                                -1.0 / 1680, 1.0 / 1188,      -691.0 / 360360,
                                1.0 / 156,   -3617.0 / 122400};
  AD old_polynomial = coefficient[7], new_polynomial = coefficient[7],
     divided = 0;
  for (int i = 6; i >= 0; --i) {
    divided = divided * new_square + old_polynomial;
    old_polynomial = old_polynomial * old_square + coefficient[i];
    new_polynomial = new_polynomial * new_square + coefficient[i];
  }
  const AD correction_difference =
      delta_inverse *
      (new_polynomial + old_inverse * (new_inverse + old_inverse) * divided);
  return correction + increment * log(x) +
         (x + increment - .5) * log1p(increment / x) - increment +
         correction_difference;
}
inline AD log_gamma_count_increment(const AD &x, double count) {
  using std::log;
  require(std::isfinite(count) && count >= 0 && count <= 1e6 &&
              std::floor(count) == count && TMBad::Value(x) > 0 &&
              TMBad::Value(x + count) <= 2e6,
          "Gamma count ratio is outside its qualified domain", "DOMAIN_ERROR");
  if (count <= 64) {
    AD value = 0;
    for (int k = 0; k < static_cast<int>(count); ++k)
      value += log(x + k);
    return value;
  }
  return log_gamma_increment(x, AD(count));
}
inline double trial_log_choose(double n, double y) {
  const double selected = std::min(y, n - y);
  if (selected <= 64) {
    Sum result;
    for (int k = 0; k < static_cast<int>(selected); ++k)
      result.add(std::log((n - k) / (k + 1)));
    return result.total();
  }
  return std::lgamma(n + 1) - std::lgamma(y + 1) - std::lgamma(n - y + 1);
}
inline void validate_trials(const Rows &rows, bool observed) {
  for (const auto &row : rows) {
    regression_x(row[0]);
    require(row[1] >= 0 && row[1] <= 1e6 && std::floor(row[1]) == row[1],
            "Binomial trials must be integers in [0, 1000000]", "DOMAIN_ERROR");
    if (observed)
      require(row[2] >= 0 && row[2] <= row[1] && std::floor(row[2]) == row[2],
              "Binomial successes must be integers between zero and trials",
              "DOMAIN_ERROR");
  }
}
inline Model binomial_model(bool beta_binomial = false) {
  Model model;
  auto &d = model.descriptor;
  d.id = beta_binomial ? "beta_binomial" : "binomial_logistic";
  d.fit_fields = {"x", "trials", "y"};
  d.parameter_names = {"intercept", "slope"};
  d.parameter_bounds = {{-10, 10}, {-2, 2}};
  if (beta_binomial) {
    d.parameter_names.push_back("log_precision");
    d.parameter_bounds.push_back({-4, 6});
  }
  d.predict = {
      target("response", {"x", "trials"}, false,
             "specified future trial counts and covariates",
             "count observation variance; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    validate_trials(data.rows, true);
  };
  model.objective = [beta_binomial](const ADVector &p, const Data &data) {
    using std::exp;
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const double n = row[1], y = row[2];
      if (n == 0)
        continue;
      const AD eta = p[0] + p[1] * row[0];
      const double log_choose = trial_log_choose(n, y);
      AD loss;
      if (beta_binomial) {
        const AD precision = exp(p[2]);
        AD alpha = precision * exp(-softplus(-eta));
        AD beta = precision * exp(-softplus(eta));
        double selected = y;
        if (y > n / 2) {
          std::swap(alpha, beta);
          selected = n - y;
        }
        // This equivalent beta ratio avoids subtracting two million-count
        // log-gamma values when an endpoint has nearly all probability mass.
        loss = log_gamma_increment(beta + (n - selected), alpha + selected) -
               log_gamma_increment(beta, alpha) -
               log_gamma_count_increment(alpha, selected) - log_choose;
      } else {
        loss = -log_choose + y * softplus(-eta) + (n - y) * softplus(eta);
      }
      total += data.weights[i] * loss;
    }
    return total;
  };
  model.prediction = [beta_binomial](const Vector &p, const Rows &rows,
                                     const Rows &, const std::string &, bool) {
    validate_trials(rows, false);
    Prediction result;
    for (const auto &row : rows) {
      const double eta = p[0] + p[1] * row[0];
      const double mu = stable_probability(eta),
                   complement = stable_probability(-eta);
      const double phi = beta_binomial ? std::exp(p[2]) : 0;
      const double factor = beta_binomial ? (row[1] + phi) / (1 + phi) : 1;
      result.values.push_back(
          moments(row[1] * mu, row[1] * mu * complement * factor));
    }
    return result;
  };
  return model;
}

inline Model beta_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "beta_regression";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"intercept", "slope", "log_precision"};
  d.parameter_bounds = {{-10, 10}, {-2, 2}, {-4, 6}};
  d.predict = {
      target("response", {"x"}, false, "specified future covariates",
             "beta observation variance; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows) {
      regression_x(row[0]);
      require(row[1] > 0 && row[1] < 1,
              "Beta responses must lie strictly in (0, 1)", "DOMAIN_ERROR");
    }
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    const AD phi = exp(p[2]);
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const AD eta = p[0] + p[1] * row[0];
      const AD alpha = phi * exp(-softplus(-eta));
      const AD beta = phi * exp(-softplus(eta));
      total += data.weights[i] *
               (log_gamma_positive(alpha) + log_gamma_positive(beta) -
                log_gamma_positive(phi) - (alpha - 1) * std::log(row[1]) -
                (beta - 1) * std::log1p(-row[1]));
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    for (const auto &row : rows) {
      regression_x(row[0]);
      const double eta = p[0] + p[1] * row[0];
      const double mu = stable_probability(eta),
                   complement = stable_probability(-eta);
      result.values.push_back(
          moments(mu, mu * complement / (1 + std::exp(p[2]))));
    }
    return result;
  };
  return model;
}

inline Model lognormal_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "lognormal_regression";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"log_location_intercept", "log_location_slope",
                       "log_sigma"};
  d.parameter_bounds = {{-12, 12}, {-3, 3}, {-4, 2}};
  d.predict = {
      target("response", {"x"}, false, "specified future covariates",
             "data-scale lognormal moments; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows) {
      regression_x(row[0]);
      require(row[1] > 0 && row[1] <= 1e12,
              "Lognormal response must be in (0, 1e12]", "DOMAIN_ERROR");
    }
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const double log_y = std::log(row[1]);
      const AD residual = log_y - p[0] - p[1] * row[0];
      total += data.weights[i] * (log_y + p[2] + .5 * log_two_pi +
                                  .5 * residual * residual * exp(-2 * p[2]));
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    const double sigma2 = std::exp(2 * p[2]);
    for (const auto &row : rows) {
      regression_x(row[0]);
      const double mean = std::exp(p[0] + p[1] * row[0] + .5 * sigma2);
      result.values.push_back(moments(mean, mean * mean * std::expm1(sigma2)));
    }
    return result;
  };
  return model;
}

inline Model student_t_model() {
  Model model;
  auto &d = model.descriptor;
  d.id = "student_t_regression";
  d.fit_fields = {"x", "y"};
  d.parameter_names = {"intercept", "slope", "log_scale", "log_df_minus_two"};
  d.parameter_bounds = {unbounded(), unbounded(), {-10, 10}, {-4, 6}};
  d.predict = {target("response", {"x"}, false, "specified future covariates",
                      "Student-t observation moments with df>2; parameter "
                      "uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [](const Vector &, const Data &data) {
    for (const auto &row : data.rows) {
      regression_x(row[0]);
      require(std::abs(row[1]) <= 1e12,
              "Student-t response exceeds its numerical domain",
              "DOMAIN_ERROR");
    }
  };
  model.objective = [](const ADVector &p, const Data &data) {
    using std::exp;
    using std::log;
    using std::log1p;
    const AD nu = 2 + exp(p[3]);
    const AD normalizer = p[2] + .5 * (log(nu) + log_two_pi - std::log(2.0)) +
                          log_gamma_positive(.5 * nu) -
                          log_gamma_positive(.5 * (nu + 1));
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const AD residual = row[1] - p[0] - p[1] * row[0];
      finite_result(TMBad::Value(residual));
      AD tail;
      if (std::abs(TMBad::Value(residual)) <= 1e100) {
        const AD scaled = residual * exp(-p[2]);
        tail = log1p(scaled * scaled / nu);
      } else {
        const AD magnitude = TMBad::Value(residual) >= 0 ? residual : -residual;
        tail = softplus(2 * log(magnitude) - 2 * p[2] - log(nu));
      }
      total += data.weights[i] * (normalizer + .5 * (nu + 1) * tail);
    }
    return total;
  };
  model.prediction = [](const Vector &p, const Rows &rows, const Rows &,
                        const std::string &, bool) {
    Prediction result;
    const double nu = 2 + std::exp(p[3]);
    const double variance = std::exp(2 * p[2]) * nu / (nu - 2);
    for (const auto &row : rows) {
      regression_x(row[0]);
      result.values.push_back(moments(p[0] + p[1] * row[0], variance));
    }
    return result;
  };
  return model;
}

inline AD positive_poisson_loss(const AD &eta, double y) {
  using std::exp;
  using std::expm1;
  using std::log;
  const AD mu = exp(eta);
  AD singleton_normalizer;
  if (TMBad::Value(mu) < 1e-4) {
    // mu + log((1-exp(-mu))/mu), avoiding cancellation for a singleton.
    const AD square = mu * mu;
    singleton_normalizer = .5 * mu + square / 24 - square * square / 2880 +
                           square * square * square / 181440;
  } else {
    singleton_normalizer = mu + log(-expm1(-mu)) - eta;
  }
  return singleton_normalizer - (y - 1) * eta + std::lgamma(y + 1);
}
inline std::pair<double, double> positive_poisson_moments(double mu) {
  if (mu < 1e-4) {
    const double square = mu * mu;
    const double fourth = square * square, sixth = fourth * square;
    return {1 + .5 * mu + square / 12 - fourth / 720 + sixth / 30240,
            .5 * mu + square / 6 - fourth / 180 + sixth / 5040};
  }
  const double normalization = -std::expm1(-mu);
  const double mean = mu / normalization;
  return {mean, mean * (1 - mu * std::exp(-mu) / normalization)};
}
inline Model poisson_component_model(const std::string &kind) {
  require(kind == "zero_truncated_poisson" || kind == "zero_inflated_poisson" ||
              kind == "hurdle_poisson",
          "Unknown prepared count component", "PREPARATION_ERROR");
  const bool mixture = kind != "zero_truncated_poisson";
  const bool hurdle = kind == "hurdle_poisson";
  const std::size_t exposure = mixture ? 2 : 1, response = mixture ? 3 : 2;
  Model model;
  auto &d = model.descriptor;
  d.id = kind;
  d.fit_fields = mixture ? std::vector<std::string>{"x", "z", "exposure", "y"}
                         : std::vector<std::string>{"x", "exposure", "y"};
  d.parameter_names = {"count_intercept", "count_slope"};
  d.parameter_bounds = {{-12, 12}, {-3, 3}};
  if (mixture) {
    d.parameter_names.insert(d.parameter_names.end(),
                             {"zero_intercept", "zero_slope"});
    d.parameter_bounds.insert(d.parameter_bounds.end(), {{-12, 12}, {-3, 3}});
  }
  auto future_fields = d.fit_fields;
  future_fields.pop_back();
  d.predict = {
      target("response", future_fields, false,
             "specified independent future count and zero-component covariates",
             "full response-mixture moments; parameter uncertainty excluded")};
  d.forecast = d.predict;
  model.validate = [mixture, exposure, response](const Vector &,
                                                 const Data &data) {
    validate_counts(data, exposure, response, 0);
    for (const auto &row : data.rows) {
      require(row[exposure] >= 1e-6, "Count exposure must be at least1e-6",
              "DOMAIN_ERROR");
      if (mixture)
        regression_x(row[1]);
      else
        require(row[response] >= 1, "Zero-truncated counts must be positive",
                "DOMAIN_ERROR");
    }
  };
  model.objective = [mixture, hurdle, exposure, response](const ADVector &p,
                                                          const Data &data) {
    using std::exp;
    AD total = 0;
    for (std::size_t i = 0; i < data.rows.size(); ++i) {
      const auto &row = data.rows[i];
      const double y = row[response];
      const AD eta = p[0] + p[1] * row[0] + std::log(row[exposure]);
      AD loss;
      if (!mixture) {
        loss = positive_poisson_loss(eta, y);
      } else {
        const AD zero_eta = p[2] + p[3] * row[1];
        if (hurdle)
          loss = y == 0 ? softplus(-zero_eta)
                        : softplus(zero_eta) + positive_poisson_loss(eta, y);
        else
          loss = y == 0 ? -log_add(-softplus(-zero_eta),
                                   -softplus(zero_eta) - exp(eta))
                        : softplus(zero_eta) + exp(eta) - y * eta +
                              std::lgamma(y + 1);
      }
      total += data.weights[i] * loss;
    }
    return total;
  };
  model.prediction = [mixture, hurdle, exposure](const Vector &p,
                                                 const Rows &rows, const Rows &,
                                                 const std::string &, bool) {
    Prediction result;
    for (const auto &row : rows) {
      regression_x(row[0]);
      require(row[exposure] >= 1e-6 && row[exposure] <= 1e6,
              "Count prediction exposure is outside its domain",
              "DOMAIN_ERROR");
      if (mixture)
        regression_x(row[1]);
      const double mu = row[exposure] * std::exp(p[0] + p[1] * row[0]);
      const auto component = (!mixture || hurdle) ? positive_poisson_moments(mu)
                                                  : std::make_pair(mu, mu);
      const double zero_eta = mixture ? p[2] + p[3] * row[1] : 0;
      const double zero = mixture ? stable_probability(zero_eta) : 0;
      const double nonzero = mixture ? stable_probability(-zero_eta) : 1;
      const double mean = nonzero * component.first;
      const double variance = nonzero * component.second + zero * nonzero *
                                                               component.first *
                                                               component.first;
      result.values.push_back(moments(mean, variance));
    }
    return result;
  };
  return model;
}
} // namespace ds60_tmbad

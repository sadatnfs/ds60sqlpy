// SPDX-License-Identifier: MIT
#pragma once
#include "models.hpp"
#include "models_extra.hpp"
#include "../../models/custom_models.hpp"
#include <set>
namespace ds60_tmbad {
inline std::vector<Model> prepared_models() {
  std::vector<Model> result{normal_model(),
                            linear_model(),
                            poisson_model(),
                            random_intercept_model(),
                            random_intercept_model(true),
                            ar1_model(),
                            ar1_random_intercept_model(),
                            poisson_random_intercept_model(),
                            poisson_random_slope_model(),
                            bernoulli_model(),
                            negative_binomial_model(),
                            gamma_model()};
  for (auto model : custom_models())
    result.push_back(std::move(model));
  std::set<std::string> ids;
  require(result.size() <= 64, "Prepared model count exceeds its bound",
          "PREPARATION_ERROR");
  auto identifier = [](const std::string &value) {
    return !value.empty() && value.size() <= 64 &&
           std::all_of(value.begin(), value.end(), [](unsigned char c) {
             return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                    (c >= '0' && c <= '9') || c == '_';
           });
  };
  auto public_id = [&](const std::string &value) {
    return identifier(value) && value.front() >= 'a' && value.front() <= 'z' &&
           std::none_of(value.begin(), value.end(),
                        [](unsigned char c) { return c >= 'A' && c <= 'Z'; });
  };
  auto names = [&](const std::vector<std::string> &values,
                   std::size_t maximum) {
    std::set<std::string> unique;
    require(values.size() <= maximum, "Prepared field count exceeds its bound",
            "PREPARATION_ERROR");
    for (const auto &value : values)
      require(identifier(value) && unique.insert(value).second,
              "Prepared field names must be distinct identifiers",
              "PREPARATION_ERROR");
  };
  for (const auto &model : result) {
    const auto &d = model.descriptor;
    require(public_id(d.id) && identifier(d.version) && ids.insert(d.id).second,
            "Prepared model IDs must be distinct identifiers",
            "PREPARATION_ERROR");
    names(d.fit_fields, max_fields);
    names(d.parameter_names, max_parameters);
    require(d.parameter_names.size() == d.parameter_bounds.size() &&
                !d.parameter_names.empty(),
            "Prepared model shape is invalid", "PREPARATION_ERROR");
    for (const auto &bound : d.parameter_bounds)
      require(!std::isnan(bound.first) && !std::isnan(bound.second) &&
                  bound.first < bound.second,
              "Prepared parameter bounds are invalid", "PREPARATION_ERROR");
    require(d.fit_kind == "rows" || d.fit_kind == "unit",
            "Unknown prepared factorization", "PREPARATION_ERROR");
    require(d.marginalization == "none" || d.marginalization == "exact" ||
                d.marginalization == "laplace",
            "Unknown prepared marginalization", "PREPARATION_ERROR");
    require(d.unit_limit > 0 && d.unit_limit <= max_unit_rows,
            "Prepared unit bound is invalid", "PREPARATION_ERROR");
    require(d.fit_kind != "rows" || (d.random_dimension == 0 &&
                                     d.marginalization == "none" && !d.ordered),
            "Row model cannot declare dependent random effects or ordering",
            "PREPARATION_ERROR");
    require(d.derivative_orders == std::vector<int>{1} ||
                (d.derivative_orders == std::vector<int>{1, 2} &&
                 d.parameter_names.size() <= 16),
            "Prepared derivative declaration exceeds implementation",
            "PREPARATION_ERROR");
    require(d.marginalization != "laplace" ||
                (d.fit_kind == "unit" && d.random_dimension >= 1 &&
                 d.random_dimension <= 8 &&
                 d.random_dimension + d.parameter_names.size() <= 16 &&
                 d.derivative_orders == std::vector<int>{1}),
            "Prepared dense Laplace declaration is unsupported",
            "PREPARATION_ERROR");
    require(static_cast<bool>(model.objective) &&
                static_cast<bool>(model.validate),
            "Prepared model is missing its numerical contract",
            "PREPARATION_ERROR");
    for (const auto *targets : {&d.predict, &d.forecast}) {
      std::set<std::string> target_names;
      require(targets->size() <= 32, "Prepared target count exceeds its bound",
              "PREPARATION_ERROR");
      for (const auto &t : *targets) {
        require(public_id(t.name) && target_names.insert(t.name).second &&
                    model.prediction,
                "Prepared target is duplicate or lacks an implementation",
                "PREPARATION_ERROR");
        names(t.fields, max_fields);
        names(t.columns, max_fields);
        require(!t.columns.empty() && !t.conditioning.empty() &&
                    !t.uncertainty.empty() && t.conditioning.size() <= 4096 &&
                    t.uncertainty.size() <= 4096,
                "Prepared target lacks bounded output semantics",
                "PREPARATION_ERROR");
      }
    }
  }
  return result;
}
} // namespace ds60_tmbad

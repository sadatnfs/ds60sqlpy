// SPDX-License-Identifier: MIT
#pragma once
#include "ad.hpp"
#include <Eigen/Dense>

namespace ds60_tmbad {
struct LaplaceState {
  double loss = 0;
  Vector gradient;
  ModeDiagnostics diagnostics;
  Eigen::MatrixXd latent_covariance;
};
inline void validate_parameters(const Model &model, const Vector &theta) {
  const auto &d = model.descriptor;
  require(!theta.empty() && theta.size() == d.parameter_names.size() &&
              theta.size() <= max_parameters,
          "Parameter count differs from the prepared model");
  require(d.parameter_bounds.size() == theta.size(),
          "Invalid prepared parameter bounds", "MODEL_CONTRACT");
  for (std::size_t i = 0; i < theta.size(); ++i) {
    finite(theta[i]);
    require(theta[i] >= d.parameter_bounds[i].first &&
                theta[i] <= d.parameter_bounds[i].second,
            "Parameters are outside the prepared model domain", "DOMAIN_ERROR");
  }
}
inline Eigen::MatrixXd symmetric(const Eigen::MatrixXd &matrix) {
  require(matrix.allFinite(), "Curvature is nonfinite", "NONFINITE_EVALUATION");
  const double scale = std::max(1.0, matrix.cwiseAbs().maxCoeff());
  require((matrix - matrix.transpose()).cwiseAbs().maxCoeff() <= 1e-9 * scale,
          "AD curvature lost symmetry", "AD_INVARIANT");
  return 0.5 * (matrix + matrix.transpose());
}
inline LaplaceState laplace(const Model &model, const Vector &theta,
                            const Data &data) {
  const std::size_t d = theta.size(), q = model.descriptor.random_dimension;
  require(q >= 1 && q <= 8 && d + q <= 16,
          "Dense Laplace dimensions exceed the declared contract",
          "RESOURCE_LIMIT");
  Vector z(theta);
  z.resize(d + q, 0.0);
  auto joint = record_function(model.objective, data, z);
  std::vector<bool> latent_mask(d + q, false);
  for (std::size_t i = d; i < d + q; ++i)
    latent_mask[i] = true;
  auto latent_gradient = joint.JacFun(latent_mask);
  check_tape(latent_gradient);
  ModeDiagnostics diagnostics;
  diagnostics.used = true;
  Vector g;
  Eigen::MatrixXd h(q, q);
  auto curvature = [&](const Vector &point) {
    const auto derivatives = latent_gradient.Jacobian(point);
    finite_result(derivatives);
    require(derivatives.size() == q * (d + q), "Joint derivative shape differs",
            "AD_INVARIANT");
    Eigen::MatrixXd out(q, q);
    for (std::size_t i = 0; i < q; ++i)
      for (std::size_t j = 0; j < q; ++j)
        out(i, j) = derivatives[i * (d + q) + d + j];
    return symmetric(out);
  };
  bool converged = false;
  for (std::size_t iteration = 0; iteration < 80; ++iteration) {
    const double value = joint(z)[0];
    finite_result(value);
    g = latent_gradient(z);
    finite_result(g);
    diagnostics.iterations = iteration;
    diagnostics.score_inf = infinity_norm(g);
    h = curvature(z);
#ifdef DS60_NATIVE_TEST_TRACE
    std::cerr << "inner " << iteration << " loss " << value << " score "
              << diagnostics.score_inf << '\n';
#endif
    if (diagnostics.score_inf <= 1e-9) {
      converged = true;
      break;
    }
    Eigen::Map<const Eigen::VectorXd> gradient(g.data(),
                                               static_cast<Eigen::Index>(q));
    Eigen::MatrixXd direction_h = h;
    Eigen::LLT<Eigen::MatrixXd> factor;
    double damping = 0;
    bool factored = false;
    for (int trial = 0; trial < 16; ++trial) {
      direction_h = h;
      direction_h.diagonal().array() += damping;
      factor.compute(direction_h);
      if (factor.info() == Eigen::Success) {
        factored = true;
        break;
      }
      damping = damping == 0 ? 1e-6 * std::max(1.0, h.cwiseAbs().maxCoeff())
                             : damping * 10;
      ++diagnostics.damping_steps;
    }
    require(factored, "Cannot form a bounded inner Newton direction",
            "INNER_MODE_FAILURE");
    const Eigen::VectorXd step = factor.solve(-gradient);
    require(step.allFinite() && gradient.dot(step) < 0,
            "Inner direction is not finite descent", "INNER_MODE_FAILURE");
    bool accepted = false;
    double alpha = 1;
    for (std::size_t trial = 0; trial < 30; ++trial) {
      Vector candidate(z);
      bool bounded = true;
      for (std::size_t j = 0; j < q; ++j) {
        candidate[d + j] += alpha * step(j);
        bounded = bounded && std::isfinite(candidate[d + j]) &&
                  std::abs(candidate[d + j]) <= 50;
      }
      if (bounded) {
        const double proposed = joint(candidate)[0];
        bool roundoff_correction = false;
        const double roundoff =
            8 * std::numeric_limits<double>::epsilon() * (1 + std::abs(value));
        double latent_size = 0;
        for (std::size_t j = 0; j < q; ++j)
          latent_size = std::max(latent_size, std::abs(z[d + j]));
        if (damping == 0 && std::isfinite(proposed) &&
            proposed <= value + roundoff &&
            alpha * step.cwiseAbs().maxCoeff() <= 1e-7 * (1 + latent_size)) {
          const auto proposed_gradient = latent_gradient(candidate);
          finite_result(proposed_gradient);
          roundoff_correction =
              infinity_norm(proposed_gradient) < diagnostics.score_inf;
        }
        if (std::isfinite(proposed) &&
            (proposed <= value + 1e-4 * alpha * gradient.dot(step) ||
             roundoff_correction)) {
          if (roundoff_correction)
            ++diagnostics.roundoff_corrections;
          z = std::move(candidate);
          accepted = true;
          break;
        }
      }
      alpha *= 0.5;
      ++diagnostics.line_search_steps;
    }
    require(accepted, "Inner Newton line search failed", "INNER_MODE_FAILURE");
  }
  require(converged, "Inner mode did not reach its score tolerance",
          "INNER_MODE_FAILURE");
  h = curvature(z);
  Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> eigen(h);
  require(eigen.info() == Eigen::Success, "Curvature eigenvalue check failed",
          "BAD_CURVATURE");
  diagnostics.minimum_eigenvalue = eigen.eigenvalues().minCoeff();
  diagnostics.maximum_eigenvalue = eigen.eigenvalues().maxCoeff();
  require(diagnostics.minimum_eigenvalue >
              1e-10 * std::max(1.0, diagnostics.maximum_eigenvalue),
          "Inner mode lacks positive well-conditioned curvature",
          "BAD_CURVATURE");
  Eigen::LLT<Eigen::MatrixXd> factor(h);
  require(factor.info() == Eigen::Success,
          "Inner curvature factorization failed", "BAD_CURVATURE");
  double logdet = 0;
  for (std::size_t i = 0; i < q; ++i)
    logdet += 2 * std::log(factor.matrixL().coeff(i, i));
  const auto full_gradient = joint.Jacobian(z);
  const auto partial_h = latent_gradient.Jacobian(z);
  auto latent_hessian = latent_gradient.JacFun(latent_mask);
  check_tape(latent_hessian);
  const auto third = latent_hessian.Jacobian(z);
  finite_result(full_gradient);
  finite_result(partial_h);
  finite_result(third);
  require(third.size() == q * q * (d + q), "Third derivative shape differs",
          "AD_INVARIANT");
  LaplaceState result;
  result.loss = joint(z)[0] + 0.5 * logdet - 0.5 * q * log_two_pi;
  result.gradient.resize(d);
  for (std::size_t a = 0; a < d; ++a) {
    Eigen::VectorXd cross(q);
    for (std::size_t j = 0; j < q; ++j)
      cross(j) = partial_h[j * (d + q) + a];
    const Eigen::VectorXd implicit = factor.solve(-cross);
    Eigen::MatrixXd change(q, q);
    for (std::size_t i = 0; i < q; ++i) {
      for (std::size_t j = 0; j < q; ++j) {
        const auto base = (i * q + j) * (d + q);
        double total = third[base + a];
        for (std::size_t k = 0; k < q; ++k)
          total += third[base + d + k] * implicit(k);
        change(i, j) = total;
      }
    }
    double residual = 0;
    for (std::size_t k = 0; k < q; ++k)
      residual += full_gradient[d + k] * implicit(k);
    result.gradient[a] =
        full_gradient[a] + residual + 0.5 * factor.solve(change).trace();
  }
  diagnostics.mode.assign(z.begin() + static_cast<std::ptrdiff_t>(d), z.end());
  result.diagnostics = diagnostics;
  result.latent_covariance = factor.solve(Eigen::MatrixXd::Identity(q, q));
  finite_result(result.loss);
  finite_result(result.gradient);
  return result;
}
inline Evaluation evaluate(const Model &model, const Vector &theta,
                           const Data &data, double unit_weight, bool hessian) {
  validate_parameters(model, theta);
  const bool unit = model.descriptor.fit_kind == "unit";
  validate_matrix(data.rows, model.descriptor.fit_fields.size(),
                  unit ? model.descriptor.unit_limit : max_rows);
  require(!unit || !data.rows.empty(), "A complete unit cannot be empty");
  finite(unit_weight);
  require(unit_weight >= 0, "Negative unit weight");
  if (!unit) {
    require(data.weights.size() == data.rows.size(),
            "Row weights have the wrong length");
    for (double weight : data.weights) {
      finite(weight);
      require(weight >= 0, "Negative row weight");
    }
  } else {
    require(data.weights.empty(), "Complete units do not accept row weights");
  }
  model.validate(theta, data);
  Evaluation result;
  result.row_count = data.rows.size();
  result.unit_count = unit ? 1 : 0;
  Sum weight;
  if (unit)
    weight.add(unit_weight);
  else
    for (double value : data.weights)
      weight.add(value);
  result.weight_sum = weight.total();
  finite_result(result.weight_sum);
  const auto d = theta.size();
  result.gradient.assign(d, 0);
  if (hessian)
    result.hessian.assign(d * d, 0);
  if (data.rows.empty())
    return result;
  if (model.descriptor.marginalization == "laplace") {
    require(!hessian, "Laplace outer Hessians are not implemented",
            "UNSUPPORTED_OPERATION");
    auto marginal = laplace(model, theta, data);
    result.loss = marginal.loss;
    result.gradient = marginal.gradient;
    result.diagnostics = marginal.diagnostics;
  } else {
    auto function = record_function(model.objective, data, theta);
    result.loss = function(theta)[0];
    result.gradient = function.Jacobian(theta);
    if (hessian) {
      require(d <= 16, "Dense Hessian exceeds its parameter limit",
              "RESOURCE_LIMIT");
      auto gradient = function.JacFun();
      check_tape(gradient);
      result.hessian = gradient.Jacobian(theta);
    }
  }
  if (unit) {
    result.loss *= unit_weight;
    for (auto &value : result.gradient)
      value *= unit_weight;
    for (auto &value : result.hessian)
      value *= unit_weight;
  }
  finite_result(result.loss);
  finite_result(result.gradient);
  finite_result(result.hessian);
  return result;
}
} // namespace ds60_tmbad

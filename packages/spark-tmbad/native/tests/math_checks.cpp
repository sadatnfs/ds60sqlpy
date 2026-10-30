// SPDX-License-Identifier: MIT
#include "ds60_tmbad/models.hpp"
#include <iostream>
using namespace ds60_tmbad;
void near(double actual, double expected, double tolerance = 1e-7) {
  if (!std::isfinite(actual) ||
      std::abs(actual - expected) > tolerance * (1 + std::abs(expected)))
    throw std::runtime_error("Independent numerical oracle mismatch");
}
int main() {
  std::string stage = "weighted Gaussian";
  try {
    const Data rows{{{1}, {2}, {4}, {7}}, {1, 2, 0.5, 3}};
    const Vector theta{2.2, 0.3};
    const auto normal = evaluate(normal_model(), theta, rows, 1, true);
    double weight = 0, residual = 0, squared = 0;
    for (std::size_t i = 0; i < rows.rows.size(); ++i) {
      const double r = theta[0] - rows.rows[i][0];
      weight += rows.weights[i];
      residual += rows.weights[i] * r;
      squared += rows.weights[i] * r * r;
    }
    const double inverse = std::exp(-2 * theta[1]);
    near(normal.loss,
         weight * (theta[1] + .5 * log_two_pi) + .5 * squared * inverse);
    near(normal.gradient[0], residual * inverse);
    near(normal.gradient[1], weight - squared * inverse);
    near(normal.hessian[0], weight * inverse);
    near(normal.hessian[1], -2 * residual * inverse);
    near(normal.hessian[2], normal.hessian[1]);
    near(normal.hessian[3], 2 * squared * inverse);
    stage = "Gaussian Laplace";
    const Data group{{{1.1}, {2.7}, {2.2}, {4.0}}, {}};
    const Vector hyper{0.8, std::log(.7), std::log(1.1)};
    const auto exact =
        evaluate(random_intercept_model(), hyper, group, 1, true);
    const auto approximate =
        evaluate(random_intercept_model(true), hyper, group, 1, false);
    near(approximate.loss, exact.loss, 1e-9);
    for (std::size_t j = 0; j < hyper.size(); ++j)
      near(approximate.gradient[j], exact.gradient[j], 1e-8);
    stage = "Poisson Laplace q1";
    const Data count{{{1, 0}, {2, 3}, {.5, 1}}, {}};
    const Vector count_theta{.2, std::log(.6)};
    const auto count_model = poisson_random_intercept_model();
    const auto count_result =
        evaluate(count_model, count_theta, count, 1, false);
    for (double step : {1e-4, 1e-5}) {
      for (std::size_t j = 0; j < count_theta.size(); ++j) {
        auto plus = count_theta, minus = count_theta;
        plus[j] += step;
        minus[j] -= step;
        const double numerical =
            (evaluate(count_model, plus, count, 1, false).loss -
             evaluate(count_model, minus, count, 1, false).loss) /
            (2 * step);
        near(count_result.gradient[j], numerical, 2e-6);
      }
    }
    stage = "Poisson Laplace q2";
    const Data slope{{{-1, 1, 0}, {0, 2, 3}, {1, .5, 1}, {2, 1, 4}}, {}};
    const Vector slope_theta{.2, .1, std::log(.6), std::log(.4)};
    const auto slope_model = poisson_random_slope_model();
    const auto slope_result =
        evaluate(slope_model, slope_theta, slope, 1, false);
    for (std::size_t j = 0; j < slope_theta.size(); ++j) {
      auto plus = slope_theta, minus = slope_theta;
      plus[j] += 1e-5;
      minus[j] -= 1e-5;
      near(slope_result.gradient[j],
           (evaluate(slope_model, plus, slope, 1, false).loss -
            evaluate(slope_model, minus, slope, 1, false).loss) /
               2e-5,
           3e-6);
    }
    stage = "Nonsymmetric vector Jacobian layout";
    Function vector_function;
    ADVector vector_input{1., 2., 3.};
    vector_function.glob.ad_start();
    TMBad::Independent(vector_input);
    ADVector vector_output{vector_input[0] +
                               2 * vector_input[1] * vector_input[1] +
                               3 * vector_input[2],
                           4 * vector_input[0] * vector_input[0] +
                               5 * vector_input[1] * vector_input[2]};
    TMBad::Dependent(vector_output);
    vector_function.glob.ad_stop();
    const auto jacobian = vector_function.Jacobian(Vector{1., 2., 3.});
    const Vector expected_jacobian{1., 8., 3., 8., 15., 10.};
    require(jacobian.size() == expected_jacobian.size(),
            "Vector Jacobian shape mismatch");
    for (std::size_t j = 0; j < jacobian.size(); ++j)
      near(jacobian[j], expected_jacobian[j], 1e-12);
    stage = "Independent dense q2 Gaussian integral";
    Model joint_gaussian;
    joint_gaussian.descriptor.id = "test_gaussian_q2";
    joint_gaussian.descriptor.fit_kind = "unit";
    joint_gaussian.descriptor.fit_fields = {"x", "y"};
    joint_gaussian.descriptor.parameter_names = {"mu", "log_sigma", "log_tau0",
                                                 "log_tau1"};
    joint_gaussian.descriptor.parameter_bounds = {
        unbounded(), {-5, 5}, {-5, 5}, {-5, 5}};
    joint_gaussian.descriptor.marginalization = "laplace";
    joint_gaussian.descriptor.random_dimension = 2;
    joint_gaussian.validate = [](const Vector &, const Data &) {};
    joint_gaussian.objective = [](const ADVector &p, const Data &data) {
      using std::exp;
      AD value = p[2] + p[3] + log_two_pi + .5 * p[4] * p[4] * exp(-2 * p[2]) +
                 .5 * p[5] * p[5] * exp(-2 * p[3]);
      for (const auto &row : data.rows) {
        const AD residual = row[1] - p[0] - p[4] - p[5] * row[0];
        value +=
            p[1] + .5 * log_two_pi + .5 * residual * residual * exp(-2 * p[1]);
      }
      return value;
    };
    const Data gaussian_data{{{-1, 2}, {0, 1}, {.5, 3}, {2, -1}}, {}};
    const Vector gaussian_theta{.4, -.3, -.1, .2};
    auto dense_gaussian = [&](const Vector &p) {
      const auto n = static_cast<Eigen::Index>(gaussian_data.rows.size());
      Eigen::VectorXd x(n), centered(n);
      for (Eigen::Index i = 0; i < n; ++i) {
        x(i) = gaussian_data.rows[i][0];
        centered(i) = gaussian_data.rows[i][1] - p[0];
      }
      Eigen::MatrixXd covariance =
          std::exp(2 * p[1]) * Eigen::MatrixXd::Identity(n, n) +
          std::exp(2 * p[2]) * Eigen::MatrixXd::Ones(n, n) +
          std::exp(2 * p[3]) * x * x.transpose();
      Eigen::LLT<Eigen::MatrixXd> factor(covariance);
      double determinant = 0;
      for (Eigen::Index i = 0; i < n; ++i)
        determinant += 2 * std::log(factor.matrixL().coeff(i, i));
      return .5 * (n * log_two_pi + determinant +
                   centered.dot(factor.solve(centered)));
    };
    const auto gaussian_result =
        evaluate(joint_gaussian, gaussian_theta, gaussian_data, 1, false);
    near(gaussian_result.loss, dense_gaussian(gaussian_theta), 1e-10);
    for (double step : {1e-4, 1e-5})
      for (std::size_t j = 0; j < gaussian_theta.size(); ++j) {
        auto plus = gaussian_theta, minus = gaussian_theta;
        plus[j] += step;
        minus[j] -= step;
        near(gaussian_result.gradient[j],
             (dense_gaussian(plus) - dense_gaussian(minus)) / (2 * step), 2e-6);
      }
    stage = "Bad latent curvature refusal";
    auto bad = random_intercept_model(true);
    bad.objective = [](const ADVector &p, const Data &) {
      return p[3] * p[3] * p[3] * p[3] - p[3] * p[3] + p[0] * p[0];
    };
    bool rejected = false;
    try {
      evaluate(bad, {0, 0, 0}, group, 1, false);
    } catch (const Error &error) {
      rejected = error.code == "BAD_CURVATURE";
    }
    require(rejected, "Nonpositive latent mode curvature was accepted");
    stage = "Failed recording context restoration";
    auto *before = TMBad::get_glob();
    try {
      record_function(
          [](const ADVector &, const Data &) -> AD {
            throw Error("TEST_FAILURE", "Deliberate test exception");
          },
          {}, {1.});
    } catch (const Error &error) {
      require(error.code == "TEST_FAILURE", "Wrong recording failure");
    }
    require(TMBad::get_glob() == before,
            "Failure left a dangling recording context");
    stage = "AR1 forecast";
    const Vector ar_theta{1, std::atanh(-.6), std::log(.4)};
    const Rows history{{8, 2}, {9, 1.3}, {10, .2}}, future{{11}, {12}, {13}};
    const auto forecast = predict(ar1_model(), ar_theta, future, history,
                                  "conditional_history", true);
    for (std::size_t j = 0; j < 3; ++j) {
      const double power = std::pow(-.6, static_cast<double>(j + 1));
      near(forecast.values[j][0], 1 + power * (.2 - 1), 1e-12);
      near(forecast.values[j][1], .16 * (1 - power * power) / (1 - .36), 1e-12);
    }
    std::cout << "PASS weighted Gaussian F/G/H; generic Gaussian/Poisson "
                 "Laplace q1/q2; nonsymmetric Jacobian; dense Gaussian "
                 "integral; curvature refusal; tape teardown; AR1 forecast\n";
  } catch (const std::exception &error) {
    std::cerr << stage << ": " << error.what() << '\n';
    return 1;
  }
}

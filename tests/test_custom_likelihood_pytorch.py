"""Source contracts and independent numeric oracles for the likelihood tutorials.

The source checks run without Torch. Numerical checks require the declared Torch
runtime and skip explicitly when it is unavailable; skipped tests are not passes.
Run with unittest inside the prepared worker, without installing test packages.
"""

from __future__ import annotations

import ast
import json
import math
import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from torch import Tensor  # type: ignore[import-not-found]  # Optional numerical test runtime.

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/custom-likelihood-pytorch"


def source(number: int) -> dict[str, Any]:
    return runpy.run_path(str(BASE / f"authoring/programs/clp-{number:03}.py"))


class SourceContract(unittest.TestCase):
    def test_complete_ordered_tutorial_and_source_parity(self) -> None:
        track = json.loads((BASE / "track.json").read_text())
        lessons = json.loads((BASE / "lessons.json").read_text())["lessons"]
        self.assertEqual(track["learning_mode"], "tutorial")
        self.assertEqual([r["id"] for r in lessons], [f"clp-{i:03}" for i in range(1, 21)])
        self.assertEqual(
            {r["level"] for r in track["lessons"]}, {"beginner", "intermediate", "advanced"}
        )
        for row in lessons:
            with self.subTest(unit=row["id"]):
                self.assertEqual(row["runtime_profile"], "llm-torch-cpu")
                self.assertEqual(row["language"], "python")
                self.assertEqual(row["solution_paths"], [])
                self.assertIsNone(row["verification_id"])
                prose = (BASE / "authoring/chapters" / (row["id"] + ".md")).read_text()
                guide = (ROOT / row["guide_path"]).read_text()
                code = (ROOT / row["source_path"]).read_text()
                self.assertGreaterEqual(len(prose.split()), 600)
                self.assertEqual(prose.count("## Worked case"), 2)
                self.assertIn("## Answered", prose)
                self.assertNotIn("\u2014", prose)
                self.assertEqual(prose.count(r"\["), prose.count(r"\]"))
                self.assertEqual(prose.count(r"\("), prose.count(r"\)"))
                self.assertIn(r"\[", prose)
                self.assertIn("```python\n" + code.rstrip() + "\n```", guide)
                self.assertEqual(
                    code, (BASE / "authoring/programs" / (row["id"] + ".py")).read_text()
                )
                ast.parse(code)
                self.assertIn("torch.float64", code)
                self.assertLess(len(code.encode()), 48000)
                self.assertNotIn("torch.cuda", code)

    def test_generator_check_has_no_drift(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BASE / "authoring/build.py"), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_evidence_boundaries_are_visible_in_learning_text(self) -> None:
        ddp = (BASE / "guides/clp-019.md").read_text()
        capstone = (BASE / "guides/clp-020.md").read_text()
        self.assertIn("serially in one CPU process", ddp)
        self.assertIn("does not initialize a process group", ddp)
        self.assertIn("supplies", capstone)
        self.assertIn("omits the covariance", capstone)
        self.assertIn("not an unbiased performance contest", capstone)


class NumericContracts(unittest.TestCase):
    torch: ClassVar[ModuleType]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            import torch
        except ImportError as exc:
            raise unittest.SkipTest("Execute numerical contracts in llm-torch-cpu") from exc
        cls.torch = torch
        cls.torch.set_num_threads(1)

    def t(self, values: object) -> Tensor:
        return self.torch.as_tensor(values, dtype=self.torch.float64)

    def close(self, actual: Tensor, expected: object, atol: float = 1e-9) -> None:
        self.torch.testing.assert_close(actual, self.t(expected), atol=atol, rtol=atol)

    def test_every_complete_program_returns_finite_diagnostics(self) -> None:
        for number in range(1, 21):
            with self.subTest(unit=number):
                result = source(number)["run_cases"]()
                self.assertGreaterEqual(len(result), 3)
                json.dumps(result, allow_nan=False)

    def test_bernoulli_at_changed_probability_and_invalid_support(self) -> None:
        f = source(1)["bernoulli_nll"]
        p = self.t(0.7).requires_grad_()
        y = [0, 1, 0, 1, 1]
        self.close(f(p, y), -3 * math.log(0.7) - 2 * math.log(0.3))
        derivative = self.torch.autograd.grad(f(p, y), p)[0]
        self.close(derivative, -3 / 0.7 + 2 / 0.3)
        for probability, observations in [(0, y), (1, y), (0.5, []), (0.5, [2])]:
            with self.assertRaises(ValueError):
                f(probability, observations)

    def test_repeated_subject_dependence_cannot_be_factored(self) -> None:
        f = source(1)["shared_subject_probability"]
        self.close(f([1, 0], [0.1, 0.9]), 0.09)
        self.assertNotAlmostEqual(float(f([1, 0], [0.1, 0.9])), 0.25)

    def test_weighted_gradient_at_new_data_and_zero_mass(self) -> None:
        f = source(2)["weighted_loss"]
        mu = self.t(1.25).requires_grad_()
        numerator, mass = f(mu, [2, -1, 5], [2, 0, 3])
        self.close(mass, 5)
        self.close(numerator, (2 * 0.75**2 + 3 * 3.75**2) / 2)
        self.close(self.torch.autograd.grad(numerator / mass, mu)[0], 1.25 - 19 / 5)
        for y, w in [([1, 2], [0, 0]), ([1, 2], [1, -1]), ([1], [1, 2])]:
            with self.assertRaises(ValueError):
                f(0, y, w)

    def test_nonlinear_gradient_matches_new_point_central_difference(self) -> None:
        ns = source(3)
        theta = self.t([1.7, 0.4]).requires_grad_()
        times, y = self.t([0.2, 1.1, 3.0]), self.t([1.5, 1.2, 0.3])

        def objective(value: Tensor) -> Tensor:
            return ns["decay_nll"](value, times, y)

        gradient = self.torch.autograd.grad(objective(theta), theta)[0]
        numeric = ns["central_difference"](objective, theta.detach(), 1e-5)
        self.close(gradient, numeric, 1e-8)

    def test_parameter_transform_has_chain_rule_but_no_likelihood_jacobian(self) -> None:
        ns = source(4)
        s = self.t(math.log(2)).requires_grad_()
        loss = ns["scale_objective"](s, self.t([1, -2, 3]))
        self.close(self.torch.autograd.grad(loss, s)[0], 3 - 14 / 4)

    def test_gaussian_fit_matches_alternative_closed_form(self) -> None:
        ns = source(5)
        x = self.t([-1, 0, 1])
        design = self.torch.stack([self.torch.ones_like(x), x], dim=1)
        y = self.t([0, 1, 3])
        result = ns["fit_gaussian"](design, y)
        # Return layout is checked against the implementation-independent OLS identities.
        fitted = result[0]
        self.close(fitted[:2], [4 / 3, 1.5], 3e-5)
        self.close(fitted[-1].exp(), math.sqrt(1 / 18), 3e-5)
        with self.assertRaises(ValueError):
            ns["fit_gaussian"](self.t([[1, 1], [2, 2], [3, 3]]), y)
        with self.assertRaises(ValueError):
            ns["fit_gaussian"](self.t([[1], [1], [1]]), self.t([2, 2, 2]))

    def test_logistic_gradient_and_hessian_at_changed_coefficients(self) -> None:
        ns = source(7)
        design = self.t([[1, -1], [1, 0.5], [1, 2]])
        y, beta = self.t([0, 1, 1]), self.t([0.4, -0.7]).requires_grad_()

        def objective(value: Tensor) -> Tensor:
            return ns["logistic_nll"](value, design, y)

        probabilities = self.torch.sigmoid(design @ beta)
        self.close(
            self.torch.autograd.grad(objective(beta), beta)[0], design.T @ (probabilities - y)
        )
        expected = design.T @ self.torch.diag(probabilities * (1 - probabilities)) @ design
        self.close(self.torch.autograd.functional.hessian(objective, beta), expected)
        with self.assertRaises(ValueError):
            ns["logistic_nll"](beta, design, self.t([0, 1, 2]))
        with self.assertRaises(ValueError):
            ns["logistic_nll"](beta, design * math.nan, y)

    def test_poisson_exposure_and_support_boundaries(self) -> None:
        ns = source(8)
        counts, exposure = self.t([1, 5]), self.t([2, 1])
        self.close(ns["fit_rate"](counts, exposure), 2)
        for bad_counts, bad_exposure in [([0, 0], [1, 1]), ([1, 2], [0, 1]), ([0.5, 1], [1, 1])]:
            with self.assertRaises(ValueError):
                ns["fit_rate"](self.t(bad_counts), self.t(bad_exposure))

    def test_censored_delayed_entry_uses_survival_denominator(self) -> None:
        ns = source(9)
        times, event, entry = self.t([2, 5, 7]), self.t([1, 0, 1]), self.t([1, 2, 3])
        self.close(ns["mle"](times, event, entry), 2 / 8)
        self.close(
            ns["censored_exponential_nll"](self.t(math.log(0.25)), times, event, entry),
            2 - 2 * math.log(0.25),
        )
        with self.assertRaises(ValueError):
            ns["mle"](times, self.t([0, 0, 0]), entry)
        with self.assertRaises(ValueError):
            ns["mle"](times, event, times)

    def test_heteroskedastic_gradient_against_manual_score(self) -> None:
        ns = source(10)
        theta = self.t([0.2, -0.1, 0.4]).requires_grad_()
        z, y = self.t([0, 1, 2]), self.t([-1, 2, 3])
        residual = theta[0] - y
        inverse_variance = self.torch.exp(-2 * (theta[1] + theta[2] * z))
        scale_score = 1 - residual.square() * inverse_variance
        expected = self.torch.stack(
            [(residual * inverse_variance).sum(), scale_score.sum(), (z * scale_score).sum()]
        )
        actual = self.torch.autograd.grad(ns["heteroskedastic_nll"](theta, z, y), theta)[0]
        self.close(actual, expected)
        with self.assertRaises(ValueError):
            ns["heteroskedastic_nll"](theta, z, self.t([1, 2]))

    def test_mixture_density_equals_independent_scalar_calculation(self) -> None:
        f = source(11)["mixture_log_prob"]
        y = 0.3
        density = 0.25 * math.exp(-((y + 1) ** 2) / 2) / math.sqrt(2 * math.pi)
        density += 0.75 * math.exp(-((y - 2) ** 2) / 8) / (2 * math.sqrt(2 * math.pi))
        self.close(
            f(
                self.t([y]),
                self.t([math.log(0.25), math.log(0.75)]),
                self.t([-1, 2]),
                self.t([1, 2]),
            ),
            [math.log(density)],
        )
        with self.assertRaises(ValueError):
            f(self.t([y]), self.t([0, 0]), self.t([-1, 2]), self.t([1, 0]))

    def test_panel_ar1_matches_conditional_innovation_factorization(self) -> None:
        ns = source(12)
        r, sigma, rho = self.t([[0.5, -0.2, 0.4, 0.1]]), 0.8, -0.3
        variance = sigma**2 * (1 - rho**2)
        expected = 0.5 * math.log(2 * math.pi * sigma**2) + float(r[0, 0] ** 2) / (2 * sigma**2)
        for i in range(1, 4):
            innovation = float(r[0, i] - rho * r[0, i - 1])
            expected += 0.5 * math.log(2 * math.pi * variance) + innovation**2 / (2 * variance)
        self.close(ns["panel_nll"](r, sigma, rho), expected)
        for bad_sigma, bad_rho in [(0, 0.5), (1, 1), (math.inf, 0.2)]:
            with self.assertRaises(ValueError):
                ns["ar1_covariance"](3, bad_sigma, bad_rho)

    def test_penalty_added_once_changes_known_minimizer(self) -> None:
        ns = source(13)
        y = self.t([2, 3, 7, 8])
        mu = self.t(20 / 7).requires_grad_()
        self.close(self.torch.autograd.grad(ns["penalized"](mu, y, 3), mu)[0], 0)

    def test_identification_and_profile_refitting(self) -> None:
        result = source(14)["run_cases"]()
        self.close(self.t(result["rank_deficient_hessian_eigenvalues"]), [0, 60])
        self.assertAlmostEqual(result["profile_rate_minimum"], 0.7)
        self.assertLess(result["short_profile_contrast"], result["long_profile_contrast"] / 1000)

    def test_closure_returns_initial_value_but_final_estimate_is_recomputed(self) -> None:
        result = source(15)["run_cases"]()["cases"]
        for name in ("lbfgs_low", "lbfgs_high"):
            self.assertGreater(result[name]["returned_step_loss"], result[name]["final_objective"])
            self.assertGreater(
                result[name]["objective_evaluations"], result[name]["optimizer_steps"]
            )
            self.assertAlmostEqual(result[name]["mean"], 1.5, places=5)

    def test_detached_graph_negative_control_is_actually_detected(self) -> None:
        result = source(16)["run_cases"]()
        self.assertTrue(result["correct_gradcheck"])
        self.assertFalse(result["detached_gradcheck"])
        self.assertTrue(result["leaf_inplace_operation_rejected"])
        self.close(self.t(result["hessian"]), [[3.2, 3], [3, 5.2]])

    def test_prediction_variance_layers_and_lognormal_estimands(self) -> None:
        result = source(17)["run_cases"]()
        at_zero = result["forecast_components"][0]
        self.assertAlmostEqual(at_zero["mean_se"] ** 2, 0.05)
        self.assertAlmostEqual(at_zero["observation_sd"] ** 2, 0.14)
        self.assertAlmostEqual(at_zero["new_group_sd"] ** 2, 0.30)
        self.assertAlmostEqual(result["lognormal_mean"], math.exp(0.58))
        self.assertAlmostEqual(result["lognormal_median"], math.exp(0.4))

    def test_exact_bootstrap_has_correct_new_empirical_variance(self) -> None:
        ns = source(18)
        values = self.t([1, 4, 7])
        samples = ns["exact_cluster_bootstrap"](values)
        self.assertEqual(len(samples), 27)
        self.close(samples.mean(), 4)
        self.close(samples.var(unbiased=False), 2)
        with self.assertRaises(ValueError):
            ns["inverse_information"](self.t([[1, 2], [2, 1]]))

    def test_ddp_scaling_and_sampler_membership_are_not_distributed_execution(self) -> None:
        result = source(19)["run_cases"]()
        self.assertIn("serial", result["execution"])
        self.assertIn("no distributed process group", result["execution"])
        padded = [i for shard in result["padded_sampler_indices"] for i in shard]
        dropped = [i for shard in result["drop_last_sampler_indices"] for i in shard]
        self.assertEqual(len(padded), 6)
        self.assertEqual(padded.count(0), 2)
        self.assertEqual(sorted(dropped), [0, 1, 2, 3])

    def test_capstone_recovery_information_and_conditional_predictions(self) -> None:
        result = source(20)["run_cases"]()
        self.close(self.t(result["parameters"]), [2.5, 0.55, 0.6], 2e-5)
        self.assertLess(result["gradient_max_abs"], 5e-4)
        self.assertGreater(result["minimum_information_eigenvalue"], 0)
        forecasts = result["conditional_group_forecasts"]
        self.assertAlmostEqual(forecasts[0][0] - forecasts[2][0], 0.5 * 0.09)
        self.assertAlmostEqual(forecasts[0][1] - forecasts[2][1], 0.25 * 0.09)
        self.assertIn("supplied covariance", result["scope"])


if __name__ == "__main__":
    unittest.main()

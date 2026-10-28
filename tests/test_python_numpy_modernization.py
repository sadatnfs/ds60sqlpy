"""Independent analytical and system invariants for NumPy units 05 through 08."""

import ast
import copy
import importlib.util
import re
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

np = pytest.importorskip("numpy")
ROOT = Path(__file__).resolve().parents[1]


def _load(number: int) -> ModuleType:
    path = ROOT / "python" / "professional" / "solutions" / f"py_numpy_{number:02d}_solution.py"
    spec = importlib.util.spec_from_file_location(f"numpy_modernization_{number}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dtypes, streams, algebra, signals = [_load(number) for number in range(5, 9)]


def test_dtypes_schema_and_copy_policy() -> None:
    source = np.arange(6, dtype=np.int16).reshape(2, 3)[:, ::-1]
    assert dtypes.numeric_schema(source) == {
        "dtype": "int16",
        "shape": (2, 3),
        "itemsize": 2,
        "bounds": (-32768, 32767),
    }
    left, right = dtypes.promote_pair(source, source)
    left[:] = -4
    assert not np.shares_memory(right, source) and not np.shares_memory(left, right)
    assert source.tolist() == [[2, 1, 0], [5, 4, 3]]
    assert dtypes.numeric_schema(np.array([], dtype=np.float32))["bounds"] is None


@pytest.mark.parametrize("raw", [np.array([True]), np.array([1 + 2j]), np.array([1], dtype=object)])
def test_dtype_contract_rejects_unsupported_storage(raw: object) -> None:
    with pytest.raises(ValueError):
        dtypes.numeric_schema(raw)
    with pytest.raises(ValueError):
        dtypes.exact_integer_sum(raw)


def test_exact_cast_and_add_across_signed_unsigned_limits() -> None:
    maximum = np.array([2**64 - 1], dtype=np.uint64)
    np.testing.assert_array_equal(dtypes.checked_integer_cast(maximum, "uint64"), maximum)
    with pytest.raises(ValueError):
        dtypes.checked_integer_cast(maximum, "int64")
    with pytest.raises(ValueError):
        dtypes.checked_integer_cast(np.array([128]), "int8")
    summed = dtypes.checked_integer_add(maximum, np.array([-(2**63)], dtype=np.int64), "int64")
    assert summed.tolist() == [2**63 - 1]
    with pytest.raises(ValueError):
        dtypes.checked_integer_add(maximum, np.array([1]), "uint64")
    result = dtypes.checked_integer_add(
        np.array([], dtype=np.int8), np.array([], dtype=np.int8), "uint16"
    )
    assert result.shape == (0,) and result.dtype == np.dtype("uint16")


def test_exact_sum_and_representability_use_mathematical_integers() -> None:
    values = np.array([2**64 - 1, 2**64 - 1], dtype=np.uint64)
    result = dtypes.exact_integer_sum(values)
    assert type(result) is int and result == 2**65 - 2
    values = np.array([-(2**63), -(2**53) - 1, -(2**53), 2**53 + 2, 2**63 - 1], dtype=np.int64)
    assert dtypes.float64_exact_mask(values).tolist() == [True, False, True, True, False]
    a, b = dtypes.promote_pair(
        np.array([2**53 + 1], dtype=np.int64), np.array([0], dtype=np.uint64)
    )
    assert a.dtype == b.dtype == np.dtype("float64") and int(a[0]) == 2**53


@pytest.mark.parametrize(
    "function,args",
    [
        (dtypes.checked_integer_cast, (np.array([1.0]), "int64")),
        (dtypes.checked_integer_cast, (np.array([1]), "float64")),
        (dtypes.checked_integer_add, (np.array([1]), np.array([[1]]), "int64")),
        (dtypes.promote_pair, (np.array([np.inf]), np.array([0.0]))),
        (dtypes.float64_exact_mask, (np.array([[1]]),)),
    ],
)
def test_dtype_boundaries(function: Callable[..., Any], args: tuple[object, ...]) -> None:
    with pytest.raises(ValueError):
        function(*args)


def test_child_streams_have_independent_state_and_reproducible_positions() -> None:
    first, second = streams.spawn_generators(111, 2)
    baseline = copy.deepcopy(second.bit_generator.state)
    first.normal(size=400)
    assert second.bit_generator.state == baseline
    expected = np.random.Generator(np.random.PCG64(np.random.SeedSequence(111).spawn(2)[1]))
    np.testing.assert_array_equal(second.random(11), expected.random(11))
    assert streams.spawn_generators(0, 0) == []


def test_task_identity_order_subset_and_seed_sum_collision() -> None:
    first = streams.simulate_task_means(41, [17, 3, 29], 37)
    assert first == streams.simulate_task_means(41, [29, 17, 3], 37)
    assert first[3] == streams.simulate_task_means(41, [3], 37)[3]
    # Two distinct seed/task pairs have the same arithmetic sum but distinct state.
    assert (
        streams.task_generator(41, 3).bit_generator.state
        != streams.task_generator(42, 2).bit_generator.state
    )
    assert streams.simulate_task_means(41, [], 37) == {}
    with pytest.raises(ValueError):
        streams.simulate_task_means(41, [3, 3], 37)


def test_paths_match_documented_draw_layout_and_consume_rng() -> None:
    rng = streams.task_generator(19, 4)
    baseline = streams.task_generator(19, 4)
    increments = baseline.normal(size=(4, 7))
    paths = streams.normal_paths(rng, 4, 7)
    assert paths.shape == (4, 8)
    np.testing.assert_array_equal(paths[:, 0], np.zeros(4))
    np.testing.assert_allclose(np.diff(paths, axis=1), increments, atol=1e-14)
    assert rng.bit_generator.state == baseline.bit_generator.state


def test_checkpoint_preserves_cached_bits_and_isolation() -> None:
    rng = streams.task_generator(71, 2)
    rng.integers(0, 100, size=3, dtype=np.uint32)
    checkpoint = streams.snapshot_rng(rng)
    before = copy.deepcopy(checkpoint)
    expected_integers = rng.integers(0, 100, size=5, dtype=np.uint32)
    expected_normal = rng.normal(size=9)
    clone = streams.restore_rng(checkpoint)
    np.testing.assert_array_equal(
        clone.integers(0, 100, size=5, dtype=np.uint32), expected_integers
    )
    np.testing.assert_array_equal(clone.normal(size=9), expected_normal)
    assert checkpoint == before
    checkpoint["bit_generator_state"]["state"]["state"] = 0
    assert rng.bit_generator.state == clone.bit_generator.state
    bad = copy.deepcopy(before)
    bad["numpy_version"] = "incompatible"
    with pytest.raises(ValueError):
        streams.restore_rng(bad)
    with pytest.raises(ValueError):
        streams.restore_rng(
            {"numpy_version": np.__version__, "bit_generator_state": {"bit_generator": "PCG64"}}
        )


@pytest.mark.parametrize(
    "function,args",
    [
        (streams.spawn_generators, (True, 2)),
        (streams.spawn_generators, (0, 1001)),
        (streams.task_generator, (0, -1)),
        (streams.task_generator, (0, 2**32)),
        (streams.normal_paths, (np.random.Generator(np.random.PCG64(0)), 1001, 1000)),
        (streams.snapshot_rng, (np.random.Generator(np.random.MT19937(0)),)),
    ],
)
def test_rng_boundaries(function: Callable[..., Any], args: tuple[object, ...]) -> None:
    with pytest.raises(ValueError):
        function(*args)


@pytest.mark.parametrize("shape", [(4, 2), (2, 4)])
def test_reduced_svd_rectangular_invariants_and_source_preservation(shape: tuple[int, int]) -> None:
    matrix = np.arange(np.prod(shape), dtype=float).reshape(shape)
    original = matrix.copy()
    u, singular, vh = algebra.reduced_svd(matrix)
    k = min(shape)
    assert u.shape == (shape[0], k) and vh.shape == (k, shape[1])
    np.testing.assert_allclose((u * singular) @ vh, original, atol=1e-12)
    np.testing.assert_allclose(u.T @ u, np.eye(k), atol=1e-12)
    np.testing.assert_allclose(vh @ vh.T, np.eye(k), atol=1e-12)
    np.testing.assert_array_equal(matrix, original)


def test_rank_threshold_is_relative_strict_and_zero_safe() -> None:
    matrix = np.diag([8.0, 2.0, 0.5])
    assert algebra.rank_at_tolerance(matrix, 0.25) == 1
    assert algebra.rank_at_tolerance(matrix * 100, 0.25) == 1
    assert algebra.rank_at_tolerance(matrix, 0.01) == 3
    assert algebra.rank_at_tolerance(np.zeros((3, 2)), 0) == 0
    with pytest.raises(ValueError):
        algebra.rank_at_tolerance(matrix, np.nan)


def test_weighted_fit_matches_weighted_mean_and_rescaling() -> None:
    design = np.ones((3, 1))
    target = np.array([2.0, 8.0, 99.0])
    weights = np.array([3.0, 1.0, 0.0])
    beta = algebra.weighted_lstsq(design, target, weights)
    np.testing.assert_allclose(beta, [3.5], atol=1e-12)
    np.testing.assert_allclose(
        algebra.weighted_lstsq(design, target, weights * 7), beta, atol=1e-12
    )
    assert np.isclose(algebra.weighted_sse(design, target, weights, beta), 27.0)
    assert algebra.weighted_sse(design, target, weights, beta + 0.1) > 27.0
    with pytest.raises(ValueError):
        algebra.weighted_lstsq(design, target, np.zeros(3))


def test_rank_deficient_minimum_norm_fit_and_objective() -> None:
    design = np.ones((3, 2))
    target = np.full(3, 6.0)
    beta = algebra.weighted_lstsq(design, target, np.ones(3))
    np.testing.assert_allclose(beta, [3, 3], atol=1e-12)
    assert algebra.weighted_sse(design, target, np.ones(3), beta) < 1e-24
    np.testing.assert_allclose(algebra.ridge_fit(design, target, 0), [3, 3], atol=1e-12)


def test_truncation_error_matches_diagonal_tail_and_rank_zero() -> None:
    matrix = np.diag([5.0, 3.0, 1.0])
    reconstructed, error = algebra.truncated_svd(matrix, 1)
    np.testing.assert_allclose(reconstructed, np.diag([5, 0, 0]), atol=1e-12)
    assert np.isclose(error, np.sqrt(10))
    zero, all_error = algebra.truncated_svd(matrix, 0)
    np.testing.assert_array_equal(zero, np.zeros_like(matrix))
    assert np.isclose(all_error, np.sqrt(35))
    full, no_tail = algebra.truncated_svd(matrix, 3)
    np.testing.assert_allclose(full, matrix, atol=1e-12)
    assert no_tail == 0
    with pytest.raises(ValueError):
        algebra.truncated_svd(matrix, True)


def test_ridge_matches_analytical_diagonal_solution_and_penalizes_intercept() -> None:
    design = np.diag([2.0, 4.0])
    target = np.array([6.0, 8.0])
    np.testing.assert_allclose(algebra.ridge_fit(design, target, 4), [1.5, 1.6], atol=1e-12)
    np.testing.assert_allclose(
        algebra.ridge_fit(np.ones((2, 1)), np.full(2, 3.0), 2), [1.5], atol=1e-12
    )
    with pytest.raises(ValueError):
        algebra.ridge_fit(design, target, -1)
    with pytest.raises(ValueError):
        algebra.reduced_svd(np.array([[np.nan]]))


def test_window_view_shares_negative_stride_source_and_rejects_writes() -> None:
    source = np.arange(6, dtype=np.int16)[::-1]
    windows = signals.window_view(source, 3)
    assert windows.shape == (4, 3) and windows.dtype == source.dtype
    assert np.shares_memory(source, windows) and not windows.flags.writeable
    with pytest.raises(ValueError):
        windows[0, 0] = 7
    source[2] = 99
    assert windows[0, 2] == windows[1, 1] == windows[2, 0] == 99
    assert source.flags.writeable


def test_asymmetric_weights_and_boundary_values_are_hand_derived() -> None:
    x = np.array([1, 2, 4], dtype=np.int64)
    weights = np.array([1, 3])
    actual = signals.weighted_valid(x, weights)
    np.testing.assert_allclose(actual, [7, 14], atol=1e-12)
    assert not np.shares_memory(actual, x)
    np.testing.assert_allclose(
        signals.convolve_same(x, np.array([1, 2, 0]), "zero"), [4, 8, 8], atol=1e-12
    )
    np.testing.assert_allclose(
        signals.convolve_same(x, np.array([1, 2, 0]), "reflect"), [4, 8, 10], atol=1e-12
    )
    # Promote before multiplying: fixed-width int64 multiplication would wrap.
    np.testing.assert_allclose(
        signals.weighted_valid(np.array([2**62]), np.array([4])), [float(2**64)]
    )


@pytest.mark.parametrize("length", [1, 5, 6, 9])
def test_real_fft_roundtrip_preserves_odd_and_even_lengths(length: int) -> None:
    source = np.arange(length, dtype=float) ** 2 - 2
    reconstructed = signals.fft_roundtrip(source)
    assert reconstructed.shape == source.shape
    np.testing.assert_allclose(reconstructed, source, atol=1e-12)


def test_one_sided_amplitude_handles_dc_even_nyquist_and_odd_last_bin() -> None:
    even = np.arange(8)
    signal = 2 + 3 * np.cos(2 * np.pi * even / 8) + 4 * (-1.0) ** even
    frequencies, amplitudes = signals.one_sided_amplitude(signal, 0.125)
    np.testing.assert_allclose(frequencies, [0, 1, 2, 3, 4], atol=1e-12)
    np.testing.assert_allclose(amplitudes, [2, 3, 0, 0, 4], atol=1e-12)
    odd = np.arange(9)
    frequencies, amplitudes = signals.one_sided_amplitude(
        5 * np.cos(2 * np.pi * 4 * odd / 9), 1 / 9
    )
    np.testing.assert_allclose(frequencies, [0, 1, 2, 3, 4], atol=1e-12)
    np.testing.assert_allclose(amplitudes, [0, 0, 0, 0, 5], atol=1e-12)


def test_fft_linear_convolution_matches_explicit_polynomial_product() -> None:
    left, right = np.array([1.0, -2.0, 3.0]), np.array([4.0, 5.0])
    # (1 - 2z + 3z**2) * (4 + 5z) = 4 - 3z + 2z**2 + 15z**3.
    np.testing.assert_allclose(signals.fft_convolve_full(left, right), [4, -3, 2, 15], atol=1e-12)
    np.testing.assert_allclose(signals.fft_convolve_full(left, np.array([1.0])), left, atol=1e-12)
    np.testing.assert_allclose(
        signals.fft_convolve_full(np.array([0.0, 1.0]), right), [0, 4, 5], atol=1e-12
    )


@pytest.mark.parametrize(
    "function,args",
    [
        (signals.window_view, (np.arange(3), True)),
        (signals.window_view, (np.arange(3), 4)),
        (signals.weighted_valid, (np.arange(3), np.ones(4))),
        (signals.convolve_same, (np.arange(3), np.ones(2), "zero")),
        (signals.convolve_same, (np.array([1]), np.ones(3), "reflect")),
        (signals.fft_roundtrip, (np.array([1 + 1j]),)),
        (signals.one_sided_amplitude, (np.ones(4), 0.0)),
        (signals.fft_convolve_full, (np.array([]), np.ones(3))),
    ],
)
def test_signal_boundaries(function: Callable[..., Any], args: tuple[object, ...]) -> None:
    with pytest.raises(ValueError):
        function(*args)


@pytest.mark.parametrize("number", [5, 6, 7, 8])
def test_six_named_contracts_match_learner_guide_and_solutions(number: int) -> None:
    stem = f"py_numpy_{number:02d}"
    directory = ROOT / "python" / "professional"
    learner = (directory / "lessons" / f"{stem}.py").read_text()
    guide = (directory / "companion-guides" / f"{stem}.md").read_text()
    explanation = (directory / "solutions" / f"{stem}_solutions.md").read_text()
    module = ast.parse(learner)
    contracts = [
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name != "worked_examples"
    ]
    assert len(contracts) == 6
    assert len(re.findall(r"^# Exercise [1-6]:", learner, re.MULTILINE)) == 6
    assert len(re.findall(r"^[1-6]\. \*\*", guide, re.MULTILINE)) == 6
    assert len(re.findall(r"^## Exercise [1-6]:", explanation, re.MULTILINE)) == 6
    for node in contracts:
        assert isinstance(node.body[-1], ast.Raise)
        assert node.name in guide and node.name in explanation
        assert hasattr(_load(number), node.name)
    assert guide.rstrip().endswith("```")
    assert "## Ask an AI tutor about this lesson" in guide
    assert "$guide-ds60sqlpy-learning" in guide
    assert "\N{EM DASH}" not in learner + guide + explanation

"""Complete offline references for python-numpy-06; explicit PCG64 state."""

import copy
from collections.abc import Callable, Sequence

import numpy as np


def _integer(value: int, name: str, minimum: int = 0, maximum: int = 2**64 - 1) -> int:
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        or not minimum <= int(value) <= maximum
    ):
        raise ValueError(f"{name} must be an integer from {minimum} through {maximum}")
    return int(value)


def _pcg64(rng: np.random.Generator) -> np.random.Generator:
    if not isinstance(rng, np.random.Generator) or type(rng.bit_generator) is not np.random.PCG64:
        raise ValueError("Expected a Generator backed by PCG64")
    return rng


def spawn_generators(seed: int, count: int) -> list[np.random.Generator]:
    seed = _integer(seed, "seed")
    count = _integer(count, "count", maximum=1000)
    children = np.random.SeedSequence(seed).spawn(count)
    return [np.random.Generator(np.random.PCG64(child)) for child in children]


def task_generator(seed: int, task_id: int) -> np.random.Generator:
    seed = _integer(seed, "seed")
    task_id = _integer(task_id, "task_id", maximum=2**32 - 1)
    sequence = np.random.SeedSequence([task_id, seed])
    return np.random.Generator(np.random.PCG64(sequence))


def normal_paths(rng: np.random.Generator, paths: int, steps: int) -> np.ndarray:
    rng = _pcg64(rng)
    paths = _integer(paths, "paths", minimum=1, maximum=1_000_000)
    steps = _integer(steps, "steps", minimum=1, maximum=1_000_000)
    if paths * steps > 1_000_000:
        raise ValueError("The fixture budget is one million increments")
    increments = rng.normal(size=(paths, steps))
    return np.column_stack((np.zeros(paths), increments.cumsum(axis=1)))


def snapshot_rng(rng: np.random.Generator) -> dict[str, object]:
    rng = _pcg64(rng)
    return {
        "numpy_version": np.__version__,
        "bit_generator_state": copy.deepcopy(rng.bit_generator.state),
    }


def restore_rng(checkpoint: dict[str, object]) -> np.random.Generator:
    if not isinstance(checkpoint, dict) or set(checkpoint) != {
        "numpy_version",
        "bit_generator_state",
    }:
        raise ValueError("Expected a complete RNG checkpoint")
    state = checkpoint["bit_generator_state"]
    if (
        checkpoint["numpy_version"] != np.__version__
        or not isinstance(state, dict)
        or state.get("bit_generator") != "PCG64"
    ):
        raise ValueError("Replay requires the same NumPy version and PCG64")
    rng = np.random.Generator(np.random.PCG64(0))
    try:
        rng.bit_generator.state = copy.deepcopy(state)
    except (TypeError, ValueError, KeyError, OverflowError) as error:
        raise ValueError("Invalid PCG64 state") from error
    return rng


def simulate_task_means(seed: int, task_ids: Sequence[int], samples: int) -> dict[int, float]:
    seed = _integer(seed, "seed")
    samples = _integer(samples, "samples", minimum=1, maximum=1_000_000)
    ids = [_integer(task, "task_id", maximum=2**32 - 1) for task in task_ids]
    if len(ids) > 1000 or len(set(ids)) != len(ids):
        raise ValueError("Expected at most 1000 unique task identities")
    return {task: float(task_generator(seed, task).normal(size=samples).mean()) for task in ids}


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    children = spawn_generators(57, 2)
    repeated = spawn_generators(57, 2)
    for child, replayed_child in zip(children, repeated, strict=True):
        np.testing.assert_array_equal(
            child.integers(1000, size=12), replayed_child.integers(1000, size=12)
        )
    assert spawn_generators(57, 0) == []
    expect_value_error(lambda: spawn_generators(True, 2))
    np.testing.assert_array_equal(task_generator(57, 7).random(9), task_generator(57, 7).random(9))
    paths = normal_paths(task_generator(57, 7), 3, 4)
    assert paths.shape == (3, 5) and np.all(paths[:, 0] == 0)
    expect_value_error(lambda: normal_paths(task_generator(57, 7), 0, 4))
    rng = task_generator(57, 12)
    rng.integers(10, size=3, dtype=np.uint32)
    checkpoint = snapshot_rng(rng)
    expected = rng.normal(size=20)
    clone = restore_rng(checkpoint)
    np.testing.assert_array_equal(clone.normal(size=20), expected)
    assert checkpoint == snapshot_rng(restore_rng(checkpoint))
    invalid = copy.deepcopy(checkpoint)
    invalid["numpy_version"] = "different"
    expect_value_error(lambda: restore_rng(invalid))
    first = simulate_task_means(57, [5, 9, 2], 100)
    second = simulate_task_means(57, [2, 5, 9], 100)
    assert first == second and simulate_task_means(57, [9], 100)[9] == first[9]
    assert simulate_task_means(57, [], 100) == {}
    expect_value_error(lambda: simulate_task_means(57, [2, 2], 100))
    print("python-numpy-06: six stream identity and replay contracts passed")


if __name__ == "__main__":
    main()

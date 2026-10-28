"""python-numpy-06: Reproducible Random Streams and Simulation State.

Run the two worked examples, then implement the six independent contracts.
Complete answers are kept in solutions/.
"""

from collections.abc import Sequence

import numpy as np


def spawn_generators(seed: int, count: int) -> list[np.random.Generator]:
    """
    Return count PCG64-backed NumPy Generator objects initialized from a fresh
    SeedSequence(seed).spawn(count). seed is an integer from 0 through 2**64 - 1; count is
    an integer from 0 through 1000. Reject bool and invalid ranges with ValueError. Zero
    count returns an empty list. Repeating the function recreates the same child identities
    in the same environment.
    """
    raise NotImplementedError("Implement spawn_generators")


def task_generator(seed: int, task_id: int) -> np.random.Generator:
    """
    Return a fresh PCG64 Generator initialized from SeedSequence([task_id, seed]), with
    task_id first. Require seed in 0 through 2**64 - 1 and task_id in 0 through 2**32 - 1,
    both integers excluding bool. Invalid values raise ValueError. Repeated calls for the
    same identity restart that stream; task execution order must not affect its draws.
    """
    raise NotImplementedError("Implement task_generator")


def normal_paths(rng: np.random.Generator, paths: int, steps: int) -> np.ndarray:
    """
    Accept a PCG64 Generator and integer paths and steps, each at least one, with paths *
    steps <= 1,000,000. Reject bool, wrong generator type and invalid dimensions with
    ValueError. Draw standard-normal increments in one array of shape (paths, steps), then
    return shape (paths, steps + 1) with a zero first column and cumulative increments
    across each row. Advance the supplied generator.
    """
    raise NotImplementedError("Implement normal_paths")


def snapshot_rng(rng: np.random.Generator) -> dict:
    """
    For a PCG64 Generator, return a dictionary with exactly numpy_version and
    bit_generator_state, containing np.__version__ and a deep copy of the complete bit-
    generator state. Do not consume draws or mutate the generator. Reject other generators
    with ValueError. The checkpoint is an in-memory Python mapping, not a portable JSON
    interchange promise.
    """
    raise NotImplementedError("Implement snapshot_rng")


def restore_rng(checkpoint: dict) -> np.random.Generator:
    """
    Require the exact snapshot_rng top-level keys, the current np.__version__, and PCG64
    bit-generator metadata. Construct a fresh PCG64 Generator and restore a deep copy of its
    complete state. Malformed or incompatible checkpoints raise ValueError. Preserve the
    checkpoint. Do not promise replay across NumPy versions, hardware environments, changed
    call order or changed algorithms.
    """
    raise NotImplementedError("Implement restore_rng")


def simulate_task_means(seed: int, task_ids: Sequence[int], samples: int) -> dict[int, float]:
    """
    Return a mapping from unique task_ids to the mean of samples standard-normal draws from
    task_generator(seed, task_id). Accept at most 1000 identities; samples is an integer
    from 1 through 1,000,000, excluding bool. Apply the existing seed/task ranges and reject
    duplicate or invalid IDs with ValueError. Empty task_ids returns an empty mapping. Each
    task restarts from its own stream.
    """
    raise NotImplementedError("Implement simulate_task_means")


def worked_examples() -> None:
    import numpy as np

    parent = np.random.SeedSequence(812)
    children = parent.spawn(2)
    streams = [np.random.Generator(np.random.PCG64(child)) for child in children]
    first = streams[0].integers(0, 100, size=4)
    again = np.random.Generator(np.random.PCG64(np.random.SeedSequence(812).spawn(2)[0]))
    assert np.array_equal(first, again.integers(0, 100, size=4))
    assert children[0].spawn_key == (0,) and children[1].spawn_key == (1,)
    assert parent.spawn(1)[0].spawn_key == (2,)
    print("child keys:", [child.spawn_key for child in children])

    import copy

    import numpy as np

    rng = np.random.Generator(np.random.PCG64(903))
    rng.integers(0, 20, size=3, dtype=np.uint32)
    checkpoint = copy.deepcopy(rng.bit_generator.state)
    expected = rng.uniform(-2, 2, size=5)
    replay = np.random.Generator(np.random.PCG64(0))
    replay.bit_generator.state = copy.deepcopy(checkpoint)
    assert np.array_equal(expected, replay.uniform(-2, 2, size=5))
    assert checkpoint != rng.bit_generator.state
    print("Replay matched five values in NumPy", np.__version__)


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement and check all six exercise contracts.")

# Exercise 1: Allocate child streams explicitly
# Contract: spawn_generators
# Prompt: Return count PCG64-backed NumPy Generator objects initialized from a fresh
# SeedSequence(seed).spawn(count). seed is an integer from 0 through 2**64 - 1; count is an
# integer from 0 through 1000. Reject bool and invalid ranges with ValueError. Zero count returns
# an empty list. Repeating the function recreates the same child identities in the same
# environment.
# Expected: Two calls with seed 57 and count 2 produce matching draws for corresponding children.
# Children are distinct Generator objects, and advancing one must not advance another.

# Exercise 2: Bind randomness to a stable task identity
# Contract: task_generator
# Prompt: Return a fresh PCG64 Generator initialized from SeedSequence([task_id, seed]), with
# task_id first. Require seed in 0 through 2**64 - 1 and task_id in 0 through 2**32 - 1, both
# integers excluding bool. Invalid values raise ValueError. Repeated calls for the same identity
# restart that stream; task execution order must not affect its draws.
# Expected: Task 7 under seed 57 reproduces its own draws when called before or after task 12.
# Changing task_id changes the seed input; this is probabilistic stream separation, not a
# mathematical uniqueness guarantee.

# Exercise 3: Consume state in a documented simulation layout
# Contract: normal_paths
# Prompt: Accept a PCG64 Generator and integer paths and steps, each at least one, with paths *
# steps <= 1,000,000. Reject bool, wrong generator type and invalid dimensions with ValueError.
# Draw standard-normal increments in one array of shape (paths, steps), then return shape (paths,
# steps + 1) with a zero first column and cumulative increments across each row. Advance the
# supplied generator.
# Expected: Three paths and four steps give shape (3, 5), all first-column values zero.
# Differencing columns recovers the increments produced by a cloned starting stream with
# normal(size=(3, 4)).

# Exercise 4: Capture an independent checkpoint
# Contract: snapshot_rng
# Prompt: For a PCG64 Generator, return a dictionary with exactly numpy_version and
# bit_generator_state, containing np.__version__ and a deep copy of the complete bit-generator
# state. Do not consume draws or mutate the generator. Reject other generators with ValueError.
# The checkpoint is an in-memory Python mapping, not a portable JSON interchange promise.
# Expected: Snapshot before drawing, then confirm the snapshot does not change after normal draws
# or uint32 integer draws. A new snapshot before any draws equals the first.

# Exercise 5: Replay only an explicit compatible checkpoint
# Contract: restore_rng
# Prompt: Require the exact snapshot_rng top-level keys, the current np.__version__, and PCG64
# bit-generator metadata. Construct a fresh PCG64 Generator and restore a deep copy of its
# complete state. Malformed or incompatible checkpoints raise ValueError. Preserve the checkpoint.
# Do not promise replay across NumPy versions, hardware environments, changed call order or
# changed algorithms.
# Expected: Checkpoint after three uint32 draws, draw 20 normals, restore, and obtain equal normal
# arrays in the same runtime. A mismatched version or non-PCG64 state must fail explicitly.

# Exercise 6: Prove scheduling independence with task outputs
# Contract: simulate_task_means
# Prompt: Return a mapping from unique task_ids to the mean of samples standard-normal draws from
# task_generator(seed, task_id). Accept at most 1000 identities; samples is an integer from 1
# through 1,000,000, excluding bool. Apply the existing seed/task ranges and reject duplicate or
# invalid IDs with ValueError. Empty task_ids returns an empty mapping. Each task restarts from
# its own stream.
# Expected: Results for [5, 9, 2], [2, 5, 9] and the subset [9] agree by task key with the same
# seed and sample count. Changing sample count changes the experiment and is not covered by that
# equality.

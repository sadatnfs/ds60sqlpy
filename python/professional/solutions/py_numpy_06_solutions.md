# python-numpy-06: Explained reference solutions

These answers accompany [Reproducible Random Streams and Simulation State](../companion-guides/py_numpy_06.md). Compare after an honest attempt. The [complete standalone executable reference](py_numpy_06_solution.py) includes imports, shared validation helpers and a `main()` that exercises every contract. The snippets below use those helpers; run the complete reference for a fresh-process check. Each named function matches the learner artifact.

## Exercise 1: Allocate child streams explicitly

**Contract: `spawn_generators`.** Return count PCG64-backed NumPy Generator objects initialized from a fresh SeedSequence(seed).spawn(count). seed is an integer from 0 through 2**64 - 1; count is an integer from 0 through 1000. Reject bool and invalid ranges with ValueError. Zero count returns an empty list. Repeating the function recreates the same child identities in the same environment.

**Expected:** Two calls with seed 57 and count 2 produce matching draws for corresponding children. Children are distinct Generator objects, and advancing one must not advance another.

```python
def spawn_generators(seed: int, count: int) -> list[np.random.Generator]:
    seed = _integer(seed, "seed")
    count = _integer(count, "count", maximum=1000)
    children = np.random.SeedSequence(seed).spawn(count)
    return [np.random.Generator(np.random.PCG64(child)) for child in children]
```

SeedSequence mixes entropy and a child position to initialize each stream. A fresh parent restarts the tree each call, while repeated spawn calls on one existing parent allocate later children. Neither behavior assigns semantic task identities by itself. The implementation chooses explicit PCG64 to make the checkpoint protocol precise, rather than letting a future default algorithm become part of an unstated assumption.

## Exercise 2: Bind randomness to a stable task identity

**Contract: `task_generator`.** Return a fresh PCG64 Generator initialized from SeedSequence([task_id, seed]), with task_id first. Require seed in 0 through 2**64 - 1 and task_id in 0 through 2**32 - 1, both integers excluding bool. Invalid values raise ValueError. Repeated calls for the same identity restart that stream; task execution order must not affect its draws.

**Expected:** Task 7 under seed 57 reproduces its own draws when called before or after task 12. Changing task_id changes the seed input; this is probabilistic stream separation, not a mathematical uniqueness guarantee.

```python
def task_generator(seed: int, task_id: int) -> np.random.Generator:
    seed = _integer(seed, "seed")
    task_id = _integer(task_id, "task_id", maximum=2**32 - 1)
    sequence = np.random.SeedSequence([task_id, seed])
    return np.random.Generator(np.random.PCG64(sequence))
```

Use an explicit ordered integer sequence rather than seed + task_id. Addition creates collisions across distinct root/task pairs. Stable task IDs belong in a manifest, not Python hash(), process IDs or enumeration order. Putting task identity before the root seed follows the intended identity scheme, but that scheme still needs versioning if an application changes it.

## Exercise 3: Consume state in a documented simulation layout

**Contract: `normal_paths`.** Accept a PCG64 Generator and integer paths and steps, each at least one, with paths * steps <= 1,000,000. Reject bool, wrong generator type and invalid dimensions with ValueError. Draw standard-normal increments in one array of shape (paths, steps), then return shape (paths, steps + 1) with a zero first column and cumulative increments across each row. Advance the supplied generator.

**Expected:** Three paths and four steps give shape (3, 5), all first-column values zero. Differencing columns recovers the increments produced by a cloned starting stream with normal(size=(3, 4)).

```python
def normal_paths(rng: np.random.Generator, paths: int, steps: int) -> np.ndarray:
    rng = _pcg64(rng)
    paths = _integer(paths, "paths", minimum=1, maximum=1_000_000)
    steps = _integer(steps, "steps", minimum=1, maximum=1_000_000)
    if paths * steps > 1_000_000:
        raise ValueError("The fixture budget is one million increments")
    increments = rng.normal(size=(paths, steps))
    return np.column_stack((np.zeros(paths), increments.cumsum(axis=1)))
```

The layout is part of the simulation protocol. Drawing all steps of one path before the next assigns random values differently from interleaving steps across paths. Adding a zero column records the initial state without consuming an extra random draw. A cumulative path illustrates state progression; its shape and reconstruction are deterministic properties, while its particular trajectory is not a statistical quality guarantee.

## Exercise 4: Capture an independent checkpoint

**Contract: `snapshot_rng`.** For a PCG64 Generator, return a dictionary with exactly numpy_version and bit_generator_state, containing np.__version__ and a deep copy of the complete bit-generator state. Do not consume draws or mutate the generator. Reject other generators with ValueError. The checkpoint is an in-memory Python mapping, not a portable JSON interchange promise.

**Expected:** Snapshot before drawing, then confirm the snapshot does not change after normal draws or uint32 integer draws. A new snapshot before any draws equals the first.

```python
def snapshot_rng(rng: np.random.Generator) -> dict:
    rng = _pcg64(rng)
    return {
        "numpy_version": np.__version__,
        "bit_generator_state": copy.deepcopy(rng.bit_generator.state),
    }
```

The state includes more than a seed. PCG64 can retain a cached 32-bit value after an odd number of uint32 draws, so cherry-picking the main integer state loses information. Deep copying keeps nested structures independent. Application parameters and task identity should be recorded alongside this RNG checkpoint, because identical random bits cannot repair changed model equations.

## Exercise 5: Replay only an explicit compatible checkpoint

**Contract: `restore_rng`.** Require the exact snapshot_rng top-level keys, the current np.__version__, and PCG64 bit-generator metadata. Construct a fresh PCG64 Generator and restore a deep copy of its complete state. Malformed or incompatible checkpoints raise ValueError. Preserve the checkpoint. Do not promise replay across NumPy versions, hardware environments, changed call order or changed algorithms.

**Expected:** Checkpoint after three uint32 draws, draw 20 normals, restore, and obtain equal normal arrays in the same runtime. A mismatched version or non-PCG64 state must fail explicitly.

```python
def restore_rng(checkpoint: dict) -> np.random.Generator:
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
```

Restoring creates a separate cursor into the same stream position; it does not rewind the original object. The version check is a deliberately conservative compatibility policy, not a universal theorem about every NumPy release. Exact replay also depends on the distribution call sequence, arguments, dtype and environment. Unsupported checkpoints should fail before downstream results are labeled reproducible.

## Exercise 6: Prove scheduling independence with task outputs

**Contract: `simulate_task_means`.** Return a mapping from unique task_ids to the mean of samples standard-normal draws from task_generator(seed, task_id). Accept at most 1000 identities; samples is an integer from 1 through 1,000,000, excluding bool. Apply the existing seed/task ranges and reject duplicate or invalid IDs with ValueError. Empty task_ids returns an empty mapping. Each task restarts from its own stream.

**Expected:** Results for [5, 9, 2], [2, 5, 9] and the subset [9] agree by task key with the same seed and sample count. Changing sample count changes the experiment and is not covered by that equality.

```python
def simulate_task_means(seed: int, task_ids: Sequence[int], samples: int) -> dict[int, float]:
    seed = _integer(seed, "seed")
    samples = _integer(samples, "samples", minimum=1, maximum=1_000_000)
    ids = [_integer(task, "task_id", maximum=2**32 - 1) for task in task_ids]
    if len(ids) > 1000 or len(set(ids)) != len(ids):
        raise ValueError("Expected at most 1000 unique task identities")
    return {task: float(task_generator(seed, task).normal(size=samples).mean()) for task in ids}
```

The result is invariant to scheduling because no task shares a mutable generator. Compare dictionaries or keyed values rather than list positions. Reproducible retries deliberately repeat a task and must not be counted as independent Monte Carlo replications. A new independent replicate needs a distinct recorded identity. This separates deterministic execution evidence from statistical inference about simulation error.

## Verification and interpretation

The executable reference covers normal and invalid examples for these contracts. Independent tests in `tests/test_python_numpy_modernization.py` use analytical answers, invariants and changed-condition cases rather than treating the reference output as its own oracle. A reference run is evidence that the implementation meets the tested inputs; explain the relevant assumption and construct an additional counterexample before claiming independent understanding.

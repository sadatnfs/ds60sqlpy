# Reproducible Random Streams and Simulation State

## Level and prerequisites

- **Stable ID:** `python-numpy-06`.
- **Level:** Advanced. Allow about 100 minutes for explanations, prediction and practice; the estimate is not a deadline.
- **Direct prerequisite:** `python-numpy-05`, [companion guide](py_numpy_05.md).
- **Direct prerequisite:** `python-31`, [companion guide](../../ds-60day/companion-guides/day31_probability_basics.md).
- **Artifacts:** [learner script](../lessons/py_numpy_06.py) · [explained reference](../solutions/py_numpy_06_solutions.md) · [executable reference](../solutions/py_numpy_06_solution.py).

## How to run this lesson

Run `./classroom` from the repository root, choose **Python** in the shared
`/classroom` directory, and open `python-numpy-06`. Read the capability notice and
use the saved coding pad with the prepared Python Core environment. Docker
supplies Python and NumPy 2.x; no host package install or notebook kernel is
needed. Windows learners use the same entrypoint in WSL 2. Paste the complete
[learner script](../lessons/py_numpy_06.py), save it, and Run its worked
examples before attempting the six task functions. Those functions remain for
you to implement; a passing demonstration does not complete their contracts.

Each browser Run starts a fresh process. Include imports, fixtures and function
calls in the saved source, and save predictions and evidence in your notes.
Temporary arrays and generator objects do not survive the process, whereas the
browser's saved work lives in its Docker learning volume. Use only the tiny
original offline fixtures here; no download, service or database is required.
The [classroom guide](../../../docs/classroom-experience.md) explains that lifecycle.

A separately prepared contributor environment may run
`uv run --no-sync python python/professional/lessons/py_numpy_06.py`
from its checkout. Follow [contributor setup](../../../CONTRIBUTING.md) first;
that environment has separate files and does not import the browser's saved
learning volume. Keep the separate answers closed until you choose to compare
a genuine attempt.

## Learning objectives

This unit is `python-numpy-06`. Its direct prerequisites are `python-numpy-05` and `python-31`. Bring integer-validation skills, basic probability vocabulary, and an understanding that pseudorandom draws approximate sampling from a model. Open this lesson in the Docker classroom's prepared Python Core environment. Everything here is offline and bounded; no background workers, multiprocessing service or data download is needed to study scheduling behavior.

You will produce simulation outputs that remain associated with the same task when execution order changes. You will also replay the continuation of a partially consumed generator in the same runtime. These are different claims: task identity determines which stream is assigned, while state determines the position within a stream. Neither claim establishes that the model is scientifically valid or that the sample size is adequate.

By the end of this lesson, you can:

- Distinguish seed-based restart, child-stream allocation and continuation from captured state.
- Assign PCG64 streams to stable task identities so scheduling order cannot reassign draws.
- Preserve complete generator state, including cached values, without advancing the supplied stream.
- Reproduce a bounded simulation in a compatible runtime and state which algorithm, version and call-layout changes invalidate that replay claim.

## Vocabulary and concepts: entropy, stream, generator and state

**Seed:** Supplies initialization information.

**SeedSequence:** Mixes that information into initial state and can derive child sequences with distinct child identities.

**BitGenerator:** An algorithm such as PCG64 that maintains internal state and produces random bits.

**Generator:** Turns those bits into distributions through methods such as `normal`, `uniform` and `integers`.

**Stream:** The sequence obtained by advancing a particular initialized generator.

**State:** The information needed to continue from a point in that sequence. A seed is not a checkpoint after work has begun. Recreating a generator from its seed restarts it, while restoring a state continues it. A deep snapshot must include cached values as well as the main internal counters.

A task identity is an application decision. It might identify a simulation replicate or a stable partition in an experiment manifest. It should not be a process ID or a list position that changes when work is rearranged. Reproducibility needs both a deterministic algorithm and a durable rule connecting that algorithm to the application.

## Syntax anatomy and explicit ownership

`np.random.Generator(np.random.PCG64(sequence))` makes the algorithm choice visible. `np.random.SeedSequence(seed).spawn(count)` derives child initialization sequences. The `spawn_key` attribute reveals each child's path in the tree. Calling `spawn` again on the same parent advances its child-allocation counter, while constructing a fresh parent with the same seed starts that allocation again.

Pass a generator into a simulation function instead of reaching for a module-global random state. The function then has an explicit stateful input. Drawing a value consumes state even if the value is used only for debugging. A logging statement that calls `rng.random()` changes later model output; printing an already computed value does not.

Our six contracts standardize on PCG64 and record `np.__version__` in checkpoints. This makes the example's replay conditions inspectable. It deliberately does not promise bitwise equality across package upgrades, hardware environments, changed distribution algorithms, or reordered calls. Keep application parameters and the exact code with an important simulation receipt.

## Worked example: a child position is allocated state

Predict whether the third child receives key `(0,)` again or a later position. This complete example exposes the difference between reusing a parent and recreating one.

```python
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
```

Corresponding children of newly initialized parents reproduce the same draws in this environment. The second call on the existing parent allocates child key `(2,)`, because two earlier children already consumed allocation positions. This is useful for a known tree of independent simulation work, but it does not automatically make task scheduling independent.

Change the program so a worker receives children according to arrival order. If task A arrives before task B on one run and afterward on another, they can swap child positions. The child streams remain well defined, but the experiment-to-stream mapping changed. That diagnosis matters more than merely observing that all workers had a seed.

## Worked example: resume after partial consumption

The integer draw deliberately requests three uint32 values. It exercises a state component that a hand-picked seed-only checkpoint could miss. The following program is complete and can run in a fresh process.

```python
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
```

The restored object begins at the saved cursor; the original has already advanced. Changing the temporary constructor seed for `replay` does not change the continuation after its complete state is replaced. By contrast, omitting the state assignment gives a different experiment. The snapshot mapping remains independent because it was deep-copied.

Now insert one additional random draw before `expected`. The old checkpoint will no longer reproduce that later block until the same extra call is replayed. This is expected: state plus the future call sequence defines the continuation. A checkpoint cannot infer an undocumented change in the consuming program.

## Stable task identity without order dependence

The task-specific constructor uses `SeedSequence([task_id, seed])`, with the identity first. Both numbers are validated nonnegative integers, and the sequence order is part of the protocol. Do not replace the sequence with `seed + task_id`: distinct pairs can share the same sum. Do not replace the identity with Python's built-in `hash()` of a string, whose result is not a stable external identifier across processes.

Use explicit unique integer IDs from an experiment manifest. If string identities are required, define and version a deterministic encoding outside this lesson. Changing identity rules creates a new experiment even if the root seed remains unchanged. A stream-separation scheme has extremely small collision risks rather than a proof that every conceivable stream is disjoint; avoid claiming that different seeds guarantee independent scientific evidence.

Task-level generators also make retries easier to reason about. Repeating task 9 with the same parameters reconstructs its output. That repeated output is useful recovery evidence but is not another independent Monte Carlo sample. Assign a new replicate identity when additional independent simulation evidence is intended.

## Simulation layout is part of the experiment

For independent standard-normal increments \(Z_{p,t}\), a random-walk path is

\[
X_{p,0}=0,\qquad X_{p,t}=\sum_{j=1}^{t} Z_{p,j}.
\]

The `normal_paths` contract draws an array shaped `(paths, steps)` and cumulatively sums across columns. Transposing that layout, drawing one column at a time, or changing the number of paths can reassign the random values associated with a trajectory. The marginal model may still be a random walk, yet exact per-path replay is a separate property.

Useful deterministic checks include the zero initial column, the final shape, finite values, and agreement between differenced paths and increments from a cloned starting stream. Statistical checks answer another question. For independent unit-variance increments, the theoretical variance at step \(t\) is \(t\), but a tiny fixture should not be required to match that variance exactly. Avoid fragile tests that fail a correct generator because one small random sample looks unusual.

## Six exercises

Implement these functions in `python/professional/lessons/py_numpy_06.py`. Preserve checkpoints and original draws while debugging so you can compare the same state, parameters and call sequence. Record task results by key rather than relying on list order.

1. **Allocate child streams explicitly: `spawn_generators`.** Return count PCG64-backed NumPy Generator objects initialized from a fresh SeedSequence(seed).spawn(count). seed is an integer from 0 through 2**64 - 1; count is an integer from 0 through 1000. Reject bool and invalid ranges with ValueError. Zero count returns an empty list. Repeating the function recreates the same child identities in the same environment.

   **Expected:** Two calls with seed 57 and count 2 produce matching draws for corresponding children. Children are distinct Generator objects, and advancing one must not advance another.

2. **Bind randomness to a stable task identity: `task_generator`.** Return a fresh PCG64 Generator initialized from SeedSequence([task_id, seed]), with task_id first. Require seed in 0 through 2**64 - 1 and task_id in 0 through 2**32 - 1, both integers excluding bool. Invalid values raise ValueError. Repeated calls for the same identity restart that stream; task execution order must not affect its draws.

   **Expected:** Task 7 under seed 57 reproduces its own draws when called before or after task 12. Changing task_id changes the seed input; this is probabilistic stream separation, not a mathematical uniqueness guarantee.

3. **Consume state in a documented simulation layout: `normal_paths`.** Accept a PCG64 Generator and integer paths and steps, each at least one, with paths * steps <= 1,000,000. Reject bool, wrong generator type and invalid dimensions with ValueError. Draw standard-normal increments in one array of shape (paths, steps), then return shape (paths, steps + 1) with a zero first column and cumulative increments across each row. Advance the supplied generator.

   **Expected:** Three paths and four steps give shape (3, 5), all first-column values zero. Differencing columns recovers the increments produced by a cloned starting stream with normal(size=(3, 4)).

4. **Capture an independent checkpoint: `snapshot_rng`.** For a PCG64 Generator, return a dictionary with exactly numpy_version and bit_generator_state, containing np.__version__ and a deep copy of the complete bit-generator state. Do not consume draws or mutate the generator. Reject other generators with ValueError. The checkpoint is an in-memory Python mapping, not a portable JSON interchange promise.

   **Expected:** Snapshot before drawing, then confirm the snapshot does not change after normal draws or uint32 integer draws. A new snapshot before any draws equals the first.

5. **Replay only an explicit compatible checkpoint: `restore_rng`.** Require the exact snapshot_rng top-level keys, the current np.__version__, and PCG64 bit-generator metadata. Construct a fresh PCG64 Generator and restore a deep copy of its complete state. Malformed or incompatible checkpoints raise ValueError. Preserve the checkpoint. Do not promise replay across NumPy versions, hardware environments, changed call order or changed algorithms.

   **Expected:** Checkpoint after three uint32 draws, draw 20 normals, restore, and obtain equal normal arrays in the same runtime. A mismatched version or non-PCG64 state must fail explicitly.

6. **Prove scheduling independence with task outputs: `simulate_task_means`.** Return a mapping from unique task_ids to the mean of samples standard-normal draws from task_generator(seed, task_id). Accept at most 1000 identities; samples is an integer from 1 through 1,000,000, excluding bool. Apply the existing seed/task ranges and reject duplicate or invalid IDs with ValueError. Empty task_ids returns an empty mapping. Each task restarts from its own stream.

   **Expected:** Results for [5, 9, 2], [2, 5, 9] and the subset [9] agree by task key with the same seed and sample count. Changing sample count changes the experiment and is not covered by that equality.

## Common pitfalls and diagnosis

When reordered work changes a task's result, inspect the identity mapping before blaming the random algorithm. When a replay differs after only integer draws, check whether the complete state, including cached values, was preserved. When repeated runs unexpectedly agree, check whether every iteration recreates the same seed instead of continuing or selecting a new replicate.

These patterns support simulation experiments, repeated resampling, synthetic test data and independent task recovery. The in-memory checkpoint deliberately avoids a JSON compatibility promise. If later persisted, use an explicit schema that preserves large integers exactly; JavaScript-number conversion can corrupt generator state just as it can corrupt identifiers.

Explain in your own words the distinction between restarting and continuing, identify one code change that preserves task-order invariance but changes outputs, and demonstrate a duplicate-ID rejection. Continue with linear algebra when you can explain both the mechanical replay evidence and the statistical assumptions it does not establish.

## Self-check

Close the examples and answer in your own words before running a confirming case:

- After a parent has spawned two children, explain why another spawn receives a later key even though the root seed is unchanged.
- Describe what a snapshot taken after three uint32 draws must preserve to replay the next normal draws in the same runtime.
- Explain why reordering task IDs should preserve results by task key, while changing the requested sample count changes the experiment.
- Identify a debugging statement that consumes random state and a logging statement that does not.

## Next step

Continue to [SVD and weighted least squares](py_numpy_07.md) after completing its linear-algebra prerequisites. Preserve the task identity, complete state and runtime conditions when generating the numerical fixtures used in later experiments.

## Official API references

See [NumPy's parallel random-generation guidance](https://numpy.org/doc/2.4/reference/random/parallel.html) for child streams and task-derived seeding, and [the random compatibility policy](https://numpy.org/doc/2.4/reference/random/compatibility.html) for the limits of reproducibility claims.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-06: Reproducible Random Streams and Simulation State.
Read python/professional/companion-guides/py_numpy_06.md and python/professional/lessons/py_numpy_06.py. Direct prerequisites: python-numpy-05, python-31. Stay within that boundary and explain new vocabulary at a beginner-friendly pace.
Focus on Generator and PCG64, SeedSequence child streams, task identity, simulation state, checkpoint replay. Explain one mechanism, ask me to predict a concrete result, let me attempt it, provide one hint at a time, then review my numerical, shape, ownership or exception evidence. Ask retrieval questions that I answer in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use the Docker classroom's prepared Python Core environment with tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database changes, downloads or external services; do not execute any live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a changed-condition failure without copying the reference.
```

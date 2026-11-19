# torch-015: Dataset, DataLoader, collation and reproducible sampling

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-014`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Dataset defines how to retrieve an observation, while DataLoader defines batching, sampling and collation. The central investigation is concrete: Load five paired ID/value records with batch size 2 and no shuffle. The finish condition is sizes 2, 2, 1 and IDs 0..4 exactly once. ValueError before padding; token IDs must be nonnegative int64 integers. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Dataset defines how to retrieve an observation, while DataLoader defines batching, sampling and collation. The default collator stacks compatible tensors and groups compatible structures; variable-length records may need a custom collate_fn. A loader's batch count differs from the number of records, and drop_last can omit a tail. Shuffling needs a controlled generator if the ordering itself is part of a reproducible experiment.

This course uses num_workers=0 so all loading occurs in the same process and requires no extra worker startup or shared-memory assumptions. Multiple workers introduce additional random state, serialization, lifetime and platform considerations that need separate testing. A local generator separates sampler randomness from unrelated global random draws. Record IDs remain in each batch so ordering, duplication and pairing can be checked independently of loss.

## Design decisions and when to use this method

Choose Dataset for access, a sampler for the intended draw policy, and collation for the batch representation. Keep these decisions separate from model fitting. Use num_workers=0 for the default classroom so worker-process startup and external random-state behavior do not obscure the data contract.

Scale loading only after measuring where time is spent and qualifying the relevant process/platform behavior. Decide whether sampling is a permutation, sampling with replacement or a grouped policy, because their valid identity-count expectations differ. Validate token types and padding metadata at collation instead of allowing an implicit integer cast to change observations silently.

## Paired TensorFlow comparison

Compare [tf-015](../../deep-learning-tensorflow/guides/tf-015.md) after deriving the shared numerical contract.

TensorFlow tf.data combines dataset transformations and prefetching in its pipeline API. PyTorch commonly separates Dataset retrieval from DataLoader sampling/collation. Both need explicit cardinality, ordering and training-only preprocessing checks; num_workers=0 is this course's bounded default, not a throughput recommendation.

## Vocabulary and concepts

**DataLoader:** An iterator coordinating sampling, batching and collation over a dataset.

**Collation:** Combining individual observations into a batch structure.

**Sampler generator:** An explicit random-state source controlling sample order.

**Worker count:** The number of separate data-loading processes.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-015`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-015.py` under `.learning/expansion/torch-015/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

TensorDataset groups tensor components sharing the leading dimension. DataLoader(batch_size=2, shuffle=False, num_workers=0) yields three batches for five records. A seeded torch.Generator supplied to shuffling controls the sampler sequence in this runtime. A custom collator receives a list of items and must return the declared batch structure; it should not perform hidden network or file mutations.

## Trace one observation through sampling and collation

A map-style Dataset maps an index to one item. A sampler chooses indices, and a DataLoader retrieves those items and groups them through a collator. The model sees the resulting batch, not an abstract guarantee that every source record appeared exactly once. TensorDataset keeps components aligned by their common leading dimension, which is why one sampled index selects its ID and value together.

For five records and batch size two without dropping, the traversal has three batch elements with sizes 2, 2, 1. Concatenated IDs are 0..4 exactly once. Dataset length five and loader batch count three describe different stages. With drop_last=True and no shuffle, the final ID 4 is omitted. With shuffling, a different identity may land in the tail; the omission still changes the epoch population even if all produced tensor shapes are uniform.

A local torch.Generator makes the source of sampler randomness explicit. Constructing two fresh generators with seed 7 starts two equivalent sequences in the pinned runtime. Reusing one consumed generator does not reset it: the next traversal begins from later RNG state. A global manual_seed call also does not describe which later operations consume draws. Reproducibility needs the generator ownership, draw order, dataset state and runtime, not only one integer seed. [PyTorch 2.9 reproducibility notes](https://docs.pytorch.org/docs/2.9/notes/randomness.html).

Default collation can stack compatible tensor shapes, but variable-length sequences require a declared representation. For[2, 3] and[4], this helper produces Long tokens shaped(2, 2), lengths shaped(2, ), and values[[2, 3], [4, 0]] with lengths[2, 1]. The corresponding validity mask from position<length is[[True, True], [True, False]]. There are three participating tokens, not four.

Padding fills storage; it does not create an observed token. Lengths remain authoritative even if zero can occur as an actual token ID in another contract. A later embedding padding_idx, attention mask or loss mask must agree on the sentinel and validity policy. A token loss averaged over all four stored positions would give the padded slot denominator weight it did not earn. Mask polarity also belongs to the consuming API, so a valid-position mask may need inversion for an API whose True means blocked.

The repaired collator accepts nonempty sequences of nonnegative integer token IDs representable in signed int64. It rejects Boolean, floating, negative and out-of-range IDs before assigning into a Long buffer. Without that boundary, a value 2.7 could silently become 2 during assignment. A downstream embedding lookup would then process a different symbol while every tensor shape looked correct. The collator does not know the eventual vocabulary size; that additional range check belongs with the vocabulary/model contract.

Multiple workers add more state. Worker processes may have replicated dataset instances and their own Python/NumPy random generators. Iterable datasets need deliberate sharding to avoid repeated records. Platform start methods, picklable functions, resource cleanup and bounded prefetch also matter. These are reasons to qualify a multiprocessing design separately, not reasons to assume that more workers always improve throughput. The default examples create no worker processes and make no cross-platform performance claim. [PyTorch 2.9 data-loading contracts](https://docs.pytorch.org/docs/2.9/data.html).

Finally, identity checks must fit the sampling policy. A no-replacement permutation should preserve the complete ID bag. A weighted sampler with replacement may deliberately repeat IDs, so its acceptance contract concerns draw counts and weights instead. Keep the chosen policy and actual records visible before interpreting a training loss.

## Worked example / walkthrough

### Example A: Inspect retained batches

The loader preserves the final singleton by default. The ID conservation check catches missing or duplicated records that value-only statistics may hide.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def collate(sequences):
    if not sequences or any(len(sequence) == 0 for sequence in sequences):
        raise ValueError("nonempty sequences required")
    if any(
        isinstance(token, (bool, np.bool_))
        or not isinstance(token, (int, np.integer))
        or not 0 <= int(token) < 2**63
        for sequence in sequences
        for token in sequence
    ):
        raise ValueError("nonnegative int64 token IDs required")
    lengths = torch.tensor([len(sequence) for sequence in sequences], dtype=torch.long)
    batch = torch.zeros((len(sequences), int(lengths.max())), dtype=torch.long)
    for row, sequence in enumerate(sequences):
        batch[row, : len(sequence)] = torch.tensor(sequence)
    return batch, lengths


dataset = torch.utils.data.TensorDataset(torch.arange(5), torch.arange(1, 6, dtype=torch.float32))
loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=False, num_workers=0)
batches = list(loader)
assert [len(ids) for ids, values in batches] == [2, 2, 1]
assert torch.cat([ids for ids, values in batches]).tolist() == [0, 1, 2, 3, 4]
```

**Expected:** sizes 2, 2, 1 and IDs 0..4 exactly once.

### Example B: Make dropping explicit

The policy changes the effective epoch population. It may be useful for fixed shapes, but it must not be described as an identical traversal.

```python
dropped = list(torch.utils.data.DataLoader(dataset, batch_size=2, drop_last=True, num_workers=0))
assert len(dropped) == 2 and torch.cat([ids for ids, values in dropped]).tolist() == [0, 1, 2, 3]
```

**Expected:** two batches; ID 4 omitted.

### Example C: Reproduce shuffle with a local generator

A new generator recreates the starting state. Reusing one already-consumed generator would produce a later random sequence rather than a replay.

```python
def order(seed):
    generator = torch.Generator().manual_seed(seed)
    batches = torch.utils.data.DataLoader(
        dataset, batch_size=2, shuffle=True, generator=generator, num_workers=0
    )
    return torch.cat([ids for ids, values in batches]).tolist()


assert order(7) == order(7) and sorted(order(7)) == list(range(5))
```

**Expected:** same permutation; all five IDs retained.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: sizes 2, 2, 1 and IDs 0..4 exactly once. ValueError before padding; token IDs must be nonnegative int64 integers. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect retained batches.** Load five paired ID/value records with batch size 2 and no shuffle.
   **Expected:** sizes 2, 2, 1 and IDs 0..4 exactly once.
   **Verify:** Save the assertion results for exercise 1, including sizes 2, 2, 1 and IDs 0..4 exactly once.

2. **Make dropping explicit.** Set drop_last True on the same fixture.
   **Expected:** two batches; ID 4 omitted.
   **Verify:** Save the assertion results for exercise 2, including two batches; ID 4 omitted.

3. **Reproduce shuffle with a local generator.** Construct two loaders with fresh generators both seeded 7.
   **Expected:** same permutation; all five IDs retained.
   **Verify:** Save the assertion results for exercise 3, including same permutation; all five IDs retained.

4. **Collate variable-length sequences.** Pad sequences[2, 3] and[4] with zero while keeping lengths.
   **Expected:** batch[[2, 3], [4, 0]] and lengths 2, 1.
   **Verify:** Save the assertion results for exercise 4, including batch[[2, 3], [4, 0]] and lengths 2, 1.

5. **Preserve pairing after shuffle.** Load values=2*IDs with shuffling and check each batch.
   **Expected:** every target equals twice its ID.
   **Verify:** Save the assertion results for exercise 5, including every target equals twice its ID.

6. **Reject invalid sequence records.** Pass an empty sequence and floating, Boolean, negative or overflowing token IDs to the collator.
   **Expected:** ValueError before padding; token IDs must be nonnegative int64 integers.
   **Verify:** Save the assertion results for exercise 6, including ValueError before padding; token IDs must be nonnegative int64 integers.

## Common pitfalls and diagnosis

If batch shapes are inconsistent, inspect item shapes and the collator output before changing the model. If token values change during collation, check for implicit dtype conversion and reject invalid IDs before constructing the integer batch. If a padded loss looks too small, compare stored positions with valid lengths.

If a fresh-seed replay differs, inspect whether the same generator was actually reset or merely reused, whether another operation consumed it, and whether dataset transforms have separate RNG state. If records disappear, check drop_last and the sampled tail. If records repeat under multiple workers, check iterable-dataset sharding and distinguish intended replacement sampling from accidental duplication. Keep the default single-process evidence separate from an unqualified multiprocess loading claim.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain DataLoader, Collation, Sampler generator using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-014` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 DataLoader](https://docs.pytorch.org/docs/2.9/data.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why is a seed insufficient by itself?**

Reproducibility also depends on which generator consumes which draws, worker behavior, dataset state and ordering. Record the whole data contract.

**Does drop_last only change tensor shape?**

No. It can remove observations from an epoch and change metric denominators. That statistical effect must be reported.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-015, Dataset, DataLoader, collation and reproducible sampling.
Read courses/deep-learning-pytorch/guides/torch-015.md and courses/deep-learning-pytorch/lessons/torch-015.py. Direct prerequisites: `torch-014`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

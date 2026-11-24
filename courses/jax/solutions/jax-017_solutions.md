# jax-017: explained reference

The transition draws noise \(\xi_t\) from its current key, forms \(g_t=2(w_t-2)+0.01\xi_t\), updates \(v_{t+1}=0.9v_t+g_t\) and \(w_{t+1}=w_t-0.1v_{t+1}\), and returns the next key and count. Reconstructing only w generally changes the next result because v and the next draw also appear in these equations. Equal keys isolate the missing-velocity comparison.

## Solution approach

List what the transition `next_state` reads: weight, velocity, a random key and a step counter. A checkpoint that can continue training must store all four. The key is a typed array, so `save_state` writes its raw words with `jax.random.key_data` and `load_state` rebuilds it with `wrap_key_data` under the same `threefry2x32` implementation.

**Why it is correct here:** Two calls of `next_state` from zero give count 2, and the first gradient near `2 * (0 - 2) = -4` makes the velocity nonzero. Rebuilding from root 52 repeats every split and draw. A round trip preserves values, scalar shapes and dtypes. Swapping the key changes the next key data. Two more steps from the original and the restored state match, ending at count 4.

## Exercise 1: Check a nontrivial checkpoint

Saving before any update would not exercise retained history.

**Expected:** Count two and nonzero velocity.

```python
state = prepared_state()
assert int(state[3]) == 2
assert float(state[1]) != 0.0
```

**Plausible wrong approach:** Saving before any update stores zero velocity and count zero. A loader that forgot the velocity would still pass, so the lesson prepares two steps first to exercise retained history.

## Exercise 2: Replay from the same root

The transition and initialization policy are deterministic in this pinned environment.

**Expected:** Every state component agrees.

```python
compare(prepared_state(), prepared_state())
```

**Plausible wrong approach:** Saving only the weight and restarting velocity at zero changes the next update, since momentum carries 90 percent of the old velocity. The continued run would diverge from the uninterrupted one.

## Exercise 3: Validate serialization values

This isolates representation correctness from continuation arithmetic.

**Expected:** Matching reconstructed state and scalar dtypes/shapes.

```python
state = prepared_state()
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "state.npz"
    save_state(path, state)
    restored = load_state(path)
    compare(state, restored)
    assert restored[0].shape == () and restored[0].dtype == jnp.float64
```

**Plausible wrong approach:** Passing the typed key directly to `np.asarray` does not yield portable numbers. `jax.random.key_data` exposes the underlying unsigned integer words that `np.savez` can store without pickling.

## Exercise 4: Show random-state importance

A changed stream is a distinct continuation even if two rounded scalar outputs happened to be close.

**Expected:** The next key identity differs; the random transition contract has changed.

```python
state = prepared_state()
other = (state[0], state[1], jax.random.key(999, impl="threefry2x32"), state[3])
a, b = next_state(state), next_state(other)
assert not np.array_equal(
    np.asarray(jax.random.key_data(a[2])), np.asarray(jax.random.key_data(b[2]))
)
```

**Plausible wrong approach:** Rebuilding the key with a different `impl` reinterprets the stored words under another generator. The reference pins `threefry2x32` on both sides so the stream continues unchanged.

## Exercise 5: Check owned cleanup

The demonstration owns and removes its temporary artifact. It does not delete an unrelated checkpoint.

**Expected:** File exists inside the scope and is absent afterward.

```python
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "state.npz"
    save_state(path, prepared_state())
    assert path.is_file()
assert not path.exists()
```

**Plausible wrong approach:** Judging that a replaced key is harmless because the next weights look close ignores the stream. The next key data differs, so every later draw differs too, and the continuation is a different run.

## Exercise 6: Continue twice

The stored state supports repeated application of the same declared transition.

**Expected:** Matching final state with count four.

```python
state = prepared_state()
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "state.npz"
    save_state(path, state)
    restored = load_state(path)
    left, right = next_state(next_state(state)), next_state(next_state(restored))
    compare(left, right)
    assert int(right[3]) == 4
```

**Plausible wrong approach:** Writing the checkpoint to a fixed path in the working directory and deleting it by name risks removing a real file. `TemporaryDirectory` owns its file, and the check confirms it is gone afterward.

## How to verify

Run the reference and confirm `jax-017: 8 asserted cases passed`. Open the saved file with `np.load` and print the dtype of each entry: the key should be unsigned integer words and the weight float64. Then load it, take two steps, and confirm the compare helper agrees with two steps from the unsaved state.

## Scope of this evidence

If continuation differs, compare the next key, current optimizer history, dtype, update count and configuration before increasing tolerance. The current example reconstructs numerical state within one process; a fresh-process and persistent-storage acceptance test is an additional workflow, not implied by this file round trip.

Extend the contract on paper to a shuffled dataset and learning-rate schedule. Identify the extra state and a fresh-process test. Compare the separate prepared checkpoint workflows in torch-028 and tf-028 while preserving the classroom's temporary-file boundary.

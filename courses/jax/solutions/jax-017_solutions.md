# jax-017: explained reference

The transition draws noise \(\xi_t\) from its current key, forms \(g_t=2(w_t-2)+0.01\xi_t\), updates \(v_{t+1}=0.9v_t+g_t\) and \(w_{t+1}=w_t-0.1v_{t+1}\), and returns the next key and count. Reconstructing only w generally changes the next result because v and the next draw also appear in these equations. Equal keys isolate the missing-velocity comparison.

## Exercise 1: Check a nontrivial checkpoint

Saving before any update would not exercise retained history.

**Expected:** Count two and nonzero velocity.

```python
state = prepared_state()
assert int(state[3]) == 2
assert float(state[1]) != 0.0
```

## Exercise 2: Replay from the same root

The transition and initialization policy are deterministic in this pinned environment.

**Expected:** Every state component agrees.

```python
compare(prepared_state(), prepared_state())
```

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

## Scope of this evidence

If continuation differs, compare the next key, current optimizer history, dtype, update count and configuration before increasing tolerance. The current example reconstructs numerical state within one process; a fresh-process and persistent-storage acceptance test is an additional workflow, not implied by this file round trip.

Extend the contract on paper to a shuffled dataset and learning-rate schedule. Identify the extra state and a fresh-process test. Compare the separate prepared checkpoint workflows in torch-028 and tf-028 while preserving the classroom's temporary-file boundary.

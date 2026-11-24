# jax-027: explained reference

For an observation matrix \(X\in\mathbb R^{N\times D}\), a row-partition specification maps the N axis to the mesh's data axis and leaves D unpartitioned. With one physical device, its only shard contains all N rows. A Gram calculation \(X^{\mathsf T}X\) returns a D-by-D matrix; a replicated output contract describes its placement, not a change to the matrix equation.

## Solution approach

Keep three things separate: the device inventory, the layout specification and the values. The mesh is built from exactly one CPU device under the name `data`. `PartitionSpec('data', None)` says rows would be split along that axis, and the empty spec says the array is replicated. With one device both layouts store the same full table, so every task checks values or metadata, never speedup.

**Why it is correct here:** The mesh has one CPU device on its `data` axis. Placing the (3, 2) table and reading it back returns the same six values, because the array is fully addressable. The two specs compare equal to the specs they were built from. The gradient of a sum of squares is `2 * x`. A (5, 2) table keeps its global shape and its single shard holds all five rows.

## Exercise 1: Inspect mesh identity

A mesh name does not imply more than the explicitly supplied device inventory.

**Expected:** One data-axis device, CPU platform.

```python
assert mesh.shape["data"] == 1
assert all(device.platform == "cpu" for device in mesh.devices.flat)
```

**Plausible wrong approach:** Reading the axis name `data` as evidence of data parallelism assumes devices that were never supplied. The mesh shape reports one device, and that is the whole inventory.

## Exercise 2: Round-trip values

This operation is valid because the one-device array is addressable in the current process.

**Expected:** Equal host values for this fully addressable fixture.

```python
placed = jax.device_put(host, row_layout)
assert placed.is_fully_addressable
close(np.asarray(placed), host)
```

**Plausible wrong approach:** Assuming `np.asarray` always works on a sharded array ignores addressability. In a multi-process setting a process may hold only some shards; here the check `is_fully_addressable` justifies the conversion.

## Exercise 3: Inspect the specification

Their intended layout meanings differ even though one device makes their concrete storage coincide.

**Expected:** The row spec names data on axis zero; replicated spec has no partition axes.

```python
assert row_layout.spec == PartitionSpec("data", None)
assert replicated.spec == PartitionSpec()
```

**Plausible wrong approach:** Concluding that the row layout and the replicated layout are the same because their storage matches on one device erases intent. Their specs differ and would place data differently on a larger mesh.

## Exercise 4: Differentiate a placed calculation

A supported one-device placement must preserve the ordinary derivative contract.

**Expected:** Twice the original table.

```python
placed = jax.device_put(host, row_layout)
close(jax.grad(lambda x: jnp.sum(x * x))(placed), 2 * host)
```

**Plausible wrong approach:** Expecting device placement to change the derivative treats layout as part of the mathematics. The gradient of the sum of squares is still `2 * host`, whatever sharding the input carries.

## Exercise 5: Change the row count

The specification describes axis meaning rather than hard-coding the original number of observations.

**Expected:** Global shape (5,2), one local shard with all rows.

```python
other = np.arange(10.0, dtype=np.float64).reshape(5, 2)
placed = jax.device_put(other, row_layout)
assert placed.shape == (5, 2)
close(placed.addressable_shards[0].data, other)
```

**Plausible wrong approach:** Testing the layout only on the original three rows could hide a helper that hard-codes the observation count. The (5, 2) table shows the spec names axis meaning, not a fixed size.

## Exercise 6: State the evidence limit

Logical annotations and backend support do not establish unobserved hardware execution.

**Expected:** Exactly one; no multi-device scaling claim.

```python
placed = jax.device_put(host, row_layout)
assert len(placed.devices()) == 1
```

**Plausible wrong approach:** Reporting that the sharded computation scaled across devices claims hardware that did not run. `len(placed.devices())` is 1, so the lesson makes no scaling claim at all.

## How to verify

Run the reference and confirm `jax-027: 8 asserted cases passed`. Print `jax.devices()` to see the single CPU device, then print `placed.sharding` and `placed.addressable_shards[0].index` to confirm that the one shard covers every row. Comparing `replicated.spec` with `row_layout.spec` shows the only difference is the declared axis.

## Scope of this evidence

If a placed computation differs, inspect layout, global shape, local shard indexing and numerical logic independently. Do not infer communication cost or replica count from a one-device result. Multi-host addressability needs its own actual fixture.

Draw a proposed two-device row partition and a replicated parameter vector. State the expected local shapes and the reduction needed for a global gradient, then identify the hardware and process evidence missing from this one-CPU lesson.

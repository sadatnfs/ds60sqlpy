# jax-027: explained reference

For an observation matrix \(X\in\mathbb R^{N\times D}\), a row-partition specification maps the N axis to the mesh's data axis and leaves D unpartitioned. With one physical device, its only shard contains all N rows. A Gram calculation \(X^{\mathsf T}X\) returns a D-by-D matrix; a replicated output contract describes its placement, not a change to the matrix equation.

## Exercise 1: Inspect mesh identity

A mesh name does not imply more than the explicitly supplied device inventory.

**Expected:** One data-axis device, CPU platform.

```python
assert mesh.shape['data'] == 1
assert all(device.platform == 'cpu' for device in mesh.devices.flat)
```

## Exercise 2: Round-trip values

This operation is valid because the one-device array is addressable in the current process.

**Expected:** Equal host values for this fully addressable fixture.

```python
placed = jax.device_put(host, row_layout)
assert placed.is_fully_addressable
close(np.asarray(placed), host)
```

## Exercise 3: Inspect the specification

Their intended layout meanings differ even though one device makes their concrete storage coincide.

**Expected:** The row spec names data on axis zero; replicated spec has no partition axes.

```python
assert row_layout.spec == PartitionSpec('data', None)
assert replicated.spec == PartitionSpec()
```

## Exercise 4: Differentiate a placed calculation

A supported one-device placement must preserve the ordinary derivative contract.

**Expected:** Twice the original table.

```python
placed = jax.device_put(host, row_layout)
close(jax.grad(lambda x: jnp.sum(x * x))(placed), 2 * host)
```

## Exercise 5: Change the row count

The specification describes axis meaning rather than hard-coding the original number of observations.

**Expected:** Global shape (5,2), one local shard with all rows.

```python
other = np.arange(10., dtype=np.float64).reshape(5, 2)
placed = jax.device_put(other, row_layout)
assert placed.shape == (5, 2)
close(placed.addressable_shards[0].data, other)
```

## Exercise 6: State the evidence limit

Logical annotations and backend support do not establish unobserved hardware execution.

**Expected:** Exactly one; no multi-device scaling claim.

```python
placed = jax.device_put(host, row_layout)
assert len(placed.devices()) == 1
```

## Scope of this evidence

If a placed computation differs, inspect layout, global shape, local shard indexing and numerical logic independently. Do not infer communication cost or replica count from a one-device result. Multi-host addressability needs its own actual fixture.

Draw a proposed two-device row partition and a replicated parameter vector. State the expected local shapes and the reduction needed for a global gradient, then identify the hardware and process evidence missing from this one-CPU lesson.

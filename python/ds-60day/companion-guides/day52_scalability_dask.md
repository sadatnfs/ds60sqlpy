# Day 52 — Scalability with Dask (Companion Guide)

## Learning objectives
- Scale pandas/numpy workloads with Dask DataFrame/Array
- Understand lazy evaluation, compute, persist, and the scheduler
- Use clusters and dashboards for monitoring

## Why this matters
Dask lets you scale familiar Python APIs to larger-than-memory datasets.

## Core concepts and examples
### Dask DataFrame
```python
import dask.dataframe as dd
ddf = dd.read_parquet('s3://bucket/data/*.parquet')
res = (ddf[ddf.amount>0]
       .assign(unit=lambda d: d.amount/d.qty)
       .groupby('store').unit.mean()
      )
res.compute()
```

### Persist and cache
```python
cached = ddf.persist()  # keep in cluster memory
```

### Dask Array
```python
import dask.array as da
x = da.random.random((10_000, 10_000), chunks=(1000,1000))
x.mean().compute()
```

## Common pitfalls
- Using unsupported pandas ops; check for .map_partitions fallback
- Too small/too large chunk sizes; profile
- Not closing cluster; dangling processes

## Practice exercises
1) Convert a pandas pipeline to Dask and benchmark
2) Adjust chunk sizes and measure impact
3) Use the dashboard to find bottlenecks

## Further reading
- Dask: https://docs.dask.org

# Integration apache-087 complete worked notebook

Measure one actual supported path with source/image/native identity, input distribution, CPU/memory/storage/time definitions and sampling window. Keep configured limits and larger capacity forecasts distinct from measured values.

## What this capacity receipt must hold

- The Docker engine OS, architecture and total memory, as `docker info` reports them.
- Image and build cache sizes from `docker system df`, before and after the run.
- The workload input in rows and bytes, with its exact result oracle.
- The configured container limits, such as 512 MB and one CPU for the batch path.
- Peak memory and CPU as sampled, with the sampling interval and the tool used.
- Elapsed time for each run in a stated cold and warm sequence.

The capacity oracle is a consistency check rather than a target number. A peak
memory reading above the configured limit means the counter measured something
other than the container. Elapsed time with a wrong result is not a measurement
of the workload. A warm run slower than a cold run usually means another process
competed, so record what else was running. The
[shared receipt rules](../../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
docker info --format "{{.OSType}}/{{.Architecture}} {{.MemTotal}}"
docker system df
```

Both commands only read engine state. `MemTotal` is the memory the Docker
engine's virtual machine sees, which on a desktop install can be far less than
the host's physical memory. `docker system df` shows reclaimable space; a large
reclaimable figure is not permission to prune shared bases or other projects.

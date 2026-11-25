# Delta Sharing apache-079 prepared command notebook

In the copied Delta Sharing project, `plan` prints `basic Parquet/minReaderVersion1` as the supported protocol before any network call. That string is the whole compatibility promise of this client:

```bash
bash run.sh prepare
bash run.sh plan
```

On a prepared reference server, `check` refuses any reader version other than 1, partitioned files and deletion vector entries before it materializes a single row:

```bash
bash run.sh check
```

The portable client rejects unsupported protocol/features before data reads. Advanced CDF/Delta/deletion-vector behavior is omitted until a supported native client and real server exchange are qualified.

Change data feed, deletion vectors and Delta format responses stay outside this client. For those tables a refusal is the correct result, not a failure to work around.
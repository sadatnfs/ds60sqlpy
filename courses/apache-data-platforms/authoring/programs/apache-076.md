# Delta Sharing apache-076 prepared command notebook

In the copied Delta Sharing project, `plan` prints the three expected rows that the later file reads must reproduce, without contacting any server:

```bash
bash run.sh prepare
bash run.sh plan
```

During `check` against your prepared server, every signed data URL must point at a host listed in `DS60_SHARING_DATA_HOSTS`, and the recipient token is never sent to that host:

```bash
bash run.sh check
```

Check separates metadata from file retrieval, never forwards recipient Authorization to storage, and withholds signed URLs. Use a separately copied owned table for the missing-file negative experiment.

A signed URL grants temporary storage access, so the receipt keeps only the data host and file sizes or hashes. A missing file belongs in its own copied table, never in the fixture.
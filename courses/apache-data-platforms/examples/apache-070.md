# Atlas apache-070 prepared command notebook

In the copied Atlas project, `plan` shows the `transform` process with `raw` as its input and `curated` as its output. The `unrecorded` dataset has no process at all, which makes it the negative case for lineage.

```bash
bash run.sh prepare
bash run.sh plan
```

With an owned Atlas server prepared through PREPARATION.md, these actions send the payloads and then ask for lineage around `curated` in both directions to depth 3:

```bash
bash run.sh apply
bash run.sh check
```

Check requires actual raw-to-process and process-to-curated edges and excludes the intentionally unrecorded asset from that path. This is explicit API lineage, not an automatic hook result.

Until those calls run, the edges exist only in a payload. This lineage comes from explicit API entities, so no hook or crawler is being tested.
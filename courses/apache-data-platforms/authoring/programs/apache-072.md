# Atlas apache-072 prepared command notebook

Each `plan` run from the copied Atlas project prints the same qualified names, because they derive from the owner value rather than a counter. That stable key is what turns a repeated `apply` into an update instead of a duplicate.

```bash
bash run.sh prepare
bash run.sh plan
```

On a prepared owned server, run `apply` a deliberate number of times, and use `check` alone when you only want to read state back:

```bash
bash run.sh apply
bash run.sh check
```

Repeat only deliberate apply operations when studying delivery/idempotency. For persistence readback use check alone. Record source payload/revision, logical run key, actual GUIDs and notification provenance separately.

Count the apply calls you made and compare them with the GUIDs that check returns. One GUID per qualified name after several applies is the idempotent result; notification provenance is a separate observation.
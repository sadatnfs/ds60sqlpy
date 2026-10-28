# Delta Sharing apache-075 prepared command notebook

Copy the owned Delta Sharing project and follow PREPARATION.md. Delta Sharing
belongs to Delta Lake/Linux Foundation. The offline preparation actions are:

```bash
bash run.sh prepare
bash run.sh plan
```

For a separately prepared actual owned reference server and untracked recipient
profile, the bounded native Docker protocol client runs with:

```bash
bash run.sh check
```

The actual check lists the exact owned share/schema/table and requires invalid-recipient401/403 before accepting its bounded row read.

The classroom Markdown pad does not start a service. Source configuration and
unit policy fixtures are not actual reference-server receipts. Keep credentials
and signed URL query strings out of all published source and evidence.

# Delta Sharing apache-080 prepared command notebook

Keep the `plan` output from the copied Delta Sharing project as your reference copy of the three expected rows:

```bash
bash run.sh prepare
bash run.sh plan
```

After the owned server resumes or is replaced, run only `check`, and never rewrite the source table first:

```bash
bash run.sh check
```

After actual server resume/replacement, run check alone and compare the same table ID/version/rows. Never rewrite the source table during retention readback. Server outage and missing-file experiments are distinct.

A server outage fails at the control endpoint, while a missing data file fails at storage. Record which call failed and its status so the two are never merged into one result.
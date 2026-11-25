# Delta Sharing apache-075 prepared command notebook

Copy the Delta Sharing project, a Delta Lake and Linux Foundation tool rather than an Apache one, and read PREPARATION.md. `prepare` only confirms the native client image, and the first `plan` creates the owned namespace and prints the expected rows with `server_contacted` false:

```bash
bash run.sh prepare
bash run.sh plan
```

The check needs a reference server you prepared yourself and a recipient profile kept under the untracked `.workshop/` directory:

```bash
bash run.sh check
```

The actual check lists the exact owned share/schema/table and requires an invalid-recipient 401 or 403 before accepting its bounded row read.

The pad never starts a server. Keep the bearer token and any signed URL query string out of the receipt; record the listed share, schema and table names and the 401 or 403 code instead.
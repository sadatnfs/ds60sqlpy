# Atlas apache-071 prepared command notebook

The plan printed from the copied Atlas project attaches the owned `_reviewed` classification to the curated dataset only. Raw and unrecorded carry no label, so a correct classification search returns exactly one asset.

```bash
bash run.sh prepare
bash run.sh plan
```

Against a prepared owned server, `apply` sends the definition and entities, and `check` reads the curated entity back to confirm the attached label:

```bash
bash run.sh apply
bash run.sh check
```

The client reads the attached classification directly. A classification search, removal and bounded index catch-up experiment use the actual release API and need separate evidence; they do not prove data-engine enforcement.

A classification is metadata about an asset. Neither the payload nor a server answer shows that a query engine enforces it, and search catch-up after removal needs its own bounded polling record.
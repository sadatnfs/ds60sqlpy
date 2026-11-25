# Atlas apache-069 prepared command notebook

`plan` prints the definitions and entities from `client.py` without any network call: an owned DataSet subtype, a Process subtype and a classification, plus raw, curated and unrecorded datasets. Copy the Atlas project and read PREPARATION.md first, since no local server is provided.

```bash
bash run.sh prepare
bash run.sh plan
```

Only a separately prepared Atlas 2.5.0 server with fixture credentials can receive these payloads. `apply` creates any missing types and posts the entities in bulk, and `check` reads them back by qualified name:

```bash
bash run.sh apply
bash run.sh check
```

Inspect the dataset/process/classification types and stable owned qualified names. After an actual apply/check, compare GUIDs before repeating apply to observe the chosen idempotent asset contract.

A printed plan is a prepared payload, not an Atlas observation. Your receipt should hold the GUID for each qualified name after the first apply and again after the second.
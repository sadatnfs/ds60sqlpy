# Delta Sharing apache-077 prepared command notebook

`fixture-contract.json` in the copied Delta Sharing project pins version 0. These two actions confirm the client image and print the rows that version should hold:

```bash
bash run.sh prepare
bash run.sh plan
```

Against an owned server prepared at version 0, `check` sends that version with an empty `predicateHints` list and confirms the `delta-table-version` header before accepting rows:

```bash
bash run.sh check
```

The fixture contract pins version 0. Append/current-versus-history and predicate-hint experiments require a compatible actual writer/server/client and separate oracles; no hint is treated as an access policy.

Predicate hints let a server skip files; they never filter rows for security. A history test needs a writer that commits version 1 and a separate oracle for each version you read.
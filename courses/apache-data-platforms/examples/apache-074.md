# Atlas apache-074 prepared command notebook

Run `plan` in the copied Atlas project and keep its output; the qualified names it prints are the keys you look up after each lifecycle change. Step 5 of PREPARATION.md gives the stop, resume and replacement order.

```bash
bash run.sh prepare
bash run.sh plan
```

Run `apply` once before any lifecycle change, then use `check` alone after each stop, resume or replacement on the prepared server:

```bash
bash run.sh apply
bash run.sh check
```

Record actual GUIDs/edges before lifecycle changes on the separately prepared server, then run check without apply. Search/index catch-up and graph/index restore require their own bounded observations.

Matching GUIDs and edges after replacement show the graph store kept its state. Search can lag the graph, so index catch-up and a graph and index restore are separate bounded tests.
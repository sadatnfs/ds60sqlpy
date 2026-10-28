# Actual local operations and retained log state

```bash
bash run.sh status
bash run.sh logs
bash run.sh check
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh down
bash run.sh start
bash run.sh check
```

Resume must reuse the retained container. Replacement after down/start must keep
the three source records and saved cluster identity. The startup path refuses
mismatched persisted metadata rather than automatically formatting it.

```bash
bash run.sh down
```

This retains data. Only after deciding that this owned fixture is no longer needed:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

The launcher validates resource ownership and never runs global prune. A retained
volume is not replicated storage or a backup on another machine.

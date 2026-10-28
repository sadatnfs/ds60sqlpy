# Logical expiry and deletion

```bash
bash run.sh check
```

The client observes a live TTL no greater than five seconds, then polls under a
fifteen-second deadline until that known value disappears. It separately inserts
and deletes a probe key and requires logical absence. Existing retained orders
are not reset. A later empty result establishes visibility, not physical erasure.

Read the explicit TTL/delete code in `client.py` and compare the readback with
snapshot retention in `backup.py`. A snapshot can retain old SSTable components
while current reads correctly omit a deleted row. Do not reduce gc_grace_seconds
or bypass repair to make this small experiment free disk sooner.

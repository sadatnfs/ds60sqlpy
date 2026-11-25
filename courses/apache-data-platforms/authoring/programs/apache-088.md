# Integration apache-088 complete worked notebook

Assemble source/config hashes, actual image/platform identities, positive/negative results, exact resume/replacement, cleanup and explicit unsupported/prepared boundaries into one reviewable dossier. Select a coherent path rather than launching every product.

## What this dossier must hold

- One named path and the reason it was chosen over the others.
- The maintained source revision and hashes for every file the path runs.
- The image ID and native platform that produced each observation.
- The positive check, the typed negative check and their exact outputs.
- Resume and replacement results, using the same read-only checker.
- The cleanup list, naming only the experiment's containers, networks and volumes.

A reviewer should be able to rebuild every verdict in the dossier from its own
fields. Check that every observation cites the image and platform it ran on, so
an ARM64 run is never presented as AMD64 evidence. Check that each negative
result names the expected failure before the observed one. Keep any feature that
was only prepared, such as a combined streaming topology, in a separate list. The
[shared receipt rules](../../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat README.md
cat batch_snapshot.py
```

The integration README separates three routes: the actual bounded batch dossier,
a real service dossier through a qualified workshop, and prepared combined
routes. Choose one before writing anything. `batch_snapshot.py` shows the receipt
shape the batch route already writes, including the explicit false for direct
connector acceptance, which is a good model for every unsupported claim.

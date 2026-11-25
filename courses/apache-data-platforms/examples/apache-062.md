# Pinot apache-062 command notebook

This sequence from the copied Pinot project never calls `initialize`. Each `identity` call reads container, image and segment identities so you can compare them across `stop`, `resume`, `down` and `start`.

```bash
bash run.sh identity
bash run.sh stop
bash run.sh resume
bash run.sh identity
bash run.sh down
bash run.sh start
bash run.sh identity
```

These are read-only identity observations. Never call initialize after stop/resume or replacement. Compare saved service IDs, image IDs, segment metadata and exact order rows; export evidence before explicit owned-data destruction.

QUALIFICATION.md records that stop and resume kept all four role containers, and that replacement changed every container while the images, the offline segment and all query results stayed the same. Run `destroy` only after that evidence is exported.
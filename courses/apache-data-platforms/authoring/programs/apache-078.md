# Delta Sharing apache-078 prepared command notebook

The copied Delta Sharing project never stores a recipient token, and these two actions work with no profile at all. That is the safe state to begin a rotation exercise from:

```bash
bash run.sh prepare
bash run.sh plan
```

Run `check` once with the old fixture profile and once with the rotated one, both against your prepared server:

```bash
bash run.sh check
```

Rotate only fixture credentials via the real provider mechanism, then test old/new control access separately. Previously issued URLs and downloaded copies have different revocation boundaries.

Rotation stops new control calls made with the old token. URLs already issued keep working until they expire, and copies already downloaded are beyond the provider's reach.
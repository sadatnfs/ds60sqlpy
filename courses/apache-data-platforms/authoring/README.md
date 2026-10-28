# Maintained Apache/open-data sources

The chapter map defines 88 stable identities and contrasting cases. Each completed
unit adds `units/apache-NNN.json`, `chapters/apache-NNN.md` and a complete source in
`programs/`. Python sources target a prepared real library. Markdown sources are
project command notebooks and have reading runtime, with no classroom Run promise.

Run `python courses/apache-data-platforms/authoring/build.py` to refresh this
subject's guides and examples. `--check` verifies exact source/output parity.
Before all 88 units are complete these commands intentionally do not create
admission manifests. `--admit` requires the full developed route before producing
`track.json` and `lessons.json`. Runtime integration remains a separate gate.

Use `../../projects/` for project links in source chapters; the generator relocates
that explicit prefix to `../projects/` in generated guides. Test both locations.
Do not use a path that works only after generation. Never edit shared reader HTML.

The API pilot is a real-library compatibility check, not a service substitute.
See [environment decisions](ENVIRONMENTS.md) for version/platform qualification.
Every service workshop must retain independent positive, negative and restart
results before its instructions are described as qualified.

## Actual service qualification

Contributor and native CI checks use `qualify_workshop.py`, with a new absent
workspace and evidence path. Normal learners still use the Bash workshop launcher
and need no host Python. Prepare the exact native classroom images first.

```bash
python3 courses/apache-data-platforms/authoring/qualify_workshop.py arrow-flight \
  --workspace /tmp/ds60-flight-qualification-1 \
  --evidence /tmp/ds60-flight-qualification-1.json --require-ipc
python3 courses/apache-data-platforms/authoring/qualify_workshop.py streaming \
  --workspace /tmp/ds60-kafka-qualification-1 \
  --evidence /tmp/ds60-kafka-qualification-1.json --prepare
```

Flight requires prepared `data-platforms-python` and `rust-stable` images. Its
server and client use at most 1 GiB combined; the offline Rust bridge has a
256 MiB temporary compile filesystem and a 1 GiB process limit. Kafka requires
the prepared `java21` image; `--prepare` explicitly builds the checksummed official
binary alternative using the reviewed upstream archive. Its service/client share a
1 GiB container budget. The retained Kafka binary layer adds approximately
200 to 300 MiB beyond the existing Java base and downloads a 135 MB archive.
These are local fixture budgets, not production sizing guarantees.

The helper records source hashes, actual image identities, native platform,
semantic and negative observations, exact-container resume and retained-volume
replacement. It removes only the verified synthetic resources it created and
retains the receipt. Existing workspaces and evidence files are never overwritten.
Native local acceptance is ARM64; actual AMD64 execution is deferred to native
GitHub runners. No local AMD64 emulation is used.

## Complete-route admission

All 88 source units now exist. After reviewing their source and explicit project
qualification boundaries, use `python authoring/build.py --admit` from this course
directory, or the full repository-relative command from the repository root.
After first admission, the CLI preserves existing complete registration on normal
refresh/check. `--admit --check` remains an explicit equivalent. Before admission,
a normal refresh never creates registration; `outputs(admit=False)` remains the
non-admitting authoring view for tests and tooling.
A source-complete reading chapter may document a separately prepared native route;
its manifest never converts that route into an ordinary Run capability.

The native common qualifier additionally accepts `cassandra` and
`cassandra-replicated`. Both capture actual CQL/outage and read-only retained
identity checks. Single-node restore receipts are exported and byte-verified
before synthetic state destruction; failed export retains the owned state for
inspection without replay. RF3 needs the documented 8 GiB engine capacity and must
not be started alongside another heavy service pack.

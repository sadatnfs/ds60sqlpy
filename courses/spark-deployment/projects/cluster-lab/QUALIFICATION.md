# Qualification boundaries

The retained [native ARM64 receipt](qualification-arm64.json) binds the exact
runtime sources and prepared image to a real single-host Compose execution.
It is separate from classroom image publication and the independent modeling
packages' own integration receipts.

| Layer | Observed status |
| --- | --- |
| Host contracts and source/catalog | 17 focused tests passed; 18 lessons admitted; 38 generated artifacts current; Python style/AST and YAML/link checks passed |
| Compose configuration | Actual `config --quiet` passed |
| Topology | Separate master, two worker containers and client driver; two executor JVMs and both worker hostnames observed |
| Bounded fitting | 100000 rows, eight complete partitions, 1 MiB driver result setting; closed-form intercept 3 and slope 2 |
| Future inputs | x=100000/100001 produced 200003/200005; deterministic covariate extrapolation, not a conditional-history model |
| Controlled worker loss | Observed RUNNING task on worker-a, stopped that owned worker, partition 0 retried as attempt 1 on worker-b; all eight partitions and numerical oracles retained |
| Restored capacity | A new ordinary baseline again used both workers and passed |
| UI/history | Driver, master and History Server returned actual HTTP200 pages; live executor REST evidence and completed history retained |
| Lifecycle | Exact container IDs survived stop/resume; replacement changed IDs while 15 event/result files stayed byte-identical and the original completed history remained readable without resubmission |
| Cleanup | All six owned containers and both networks removed; all 51 pre-existing volumes preserved |
| Raw-collection refusal | Not run; bounded summary collection and configured maxResultSize were observed |
| Notebook | Image lock/build and actual kernel not prepared/qualified |
| JVM Standalone cluster mode | Supported version-specific instruction, not executed in this receipt |
| Kubernetes/cloud | Not run; portable instructions only |
| Modeling packages | Separately owned; this linear infrastructure fixture does not qualify their fit/predict/forecast APIs |

The aggregate container caps were 5984 MiB and 3.5 CPUs. Compute services stayed
on the internal network. Only a fixed-destination UI relay joined the separate
ingress network and published loopback ports. No engine socket, learner volume,
registry access, image download or CPU emulation was used.

Initial failed runs are retained separately. The prepared pad image's inherited
loopback binding required explicit service addresses; native zstd extraction
required executable bounded scratch; the evidence probe needed the actual UI
address; internal-only network port publication needed the narrow UI relay.
No failure was relabeled as successful execution.
